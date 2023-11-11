"""
Views for the payment app
"""
from datetime import datetime
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from login.models import CustomUser
from gold.functions import buy

from .models import TransactionDetails, AutopayModel, AuthRequest
from .serializers import TransactionSerializer, AutopaySerializer
from .functions import make_pay_request, make_response, check_checksum, decipher_callback


@api_view(["POST"])
def create_transaction(request):
    """
    DESCRIPTION
        This view will create a transaction for the given user.
    """
    user: CustomUser = request.user
    amount = request.data.get("amount")
    txn = TransactionDetails.objects.create(
        user_id=user,
        amount=amount
    )
    payload = {
        "merchantTransactionId": txn.txn_id,
        "amount": amount,
        "merchantUserId": user.user_id,
        "callbackUrl": "https://api.filit.in/payments/verify/",
        "redirectUrl": "https://filit.in/",
        "redirectMode": "REDIRECT",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    response = make_pay_request("/pg/v1/pay", payload)
    return Response(response.json())


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def verify_transaction(request):
    """
    DESCRIPTION
        This view will verify the transaction for the given user.
    """
    print("Callback received")
    try:
        if not check_checksum(request.headers["X-VERIFY"], request.data["response"]):
            print("Checksum failed")
            return Response("Invalid Checksum")
    except KeyError:
        return Response("Key Error")
    data = decipher_callback(request.data["response"])
    data = data["data"]
    txn = TransactionDetails.objects.filter(
        txn_id=data["merchantTransactionId"])
    if data["code"] == "PAYMENT_SUCCESS":
        print(data)
        if (not txn.exists() or txn.amount != data["amount"]):
            return Response("Invalid Transaction")
        txn = txn.first()
        txn.completion_status = "SUCCESS"
        txn.payment_instrument = data["paymentInstrument"]["type"]
        if data["paymentInstrument"]["type"] == "UPI":
            txn.payment_id = data["paymentInstrument"]["utr"]
        else:
            txn.payment_id = data["paymentInstrument"]["pgTransactionId"]
        txn.save()
        print("Payment Succeeded")
        return Response("Payment Succeeded")
    if txn.exists():
        txn = txn.first()
        txn.completion_status = "FAILED"
    print("Payment Failed")
    return Response("Payment Failed")


@api_view(["GET"])
def get_payments(request):
    """
    DESCRIPTION
        Get all payments for the given user
    """
    user = request.user
    txn = TransactionDetails.objects.filter(user_id=user)
    paginator = Paginator(txn, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return Response(make_response("Data fetched successfully", data={'items': TransactionSerializer(page_obj.object_list, many=True).data, 'has_next': page_obj.has_next()}))


@api_view(["POST"])
def check_payment(request):
    """
    DESCRIPTION
        Status check for payment
    """
    user = request.user
    txn_id = request.data["txn_id"]
    txn = TransactionDetails.objects.filter(user_id=user, txn_id=txn_id)
    if not txn.exists():
        return Response(make_response("Transaction doesn't exist", status=400))
    return Response(make_response("Data fetched successfully", data=TransactionSerializer(txn.first()).data))


@api_view(["GET"])
def start_subscription(request):
    """
    DESCRIPTION
        This view will start a subscription for the given user.
    parameters:
        subscriptionName
        authWorkflowType -> PENNY_DROP
        amountType -> VARIABLE
        amount -> 1500 (150000 paise) 
        frequency -> DAILY
        recurringCount -> 365
        description
        mobileNumber
    """
    user = request.user
    autopay = AutopayModel.objects.filter(user_id=user, status="ACTIVE")
    if autopay.exists():
        return Response(make_response("Subscription already exists",
                                      status=400,
                                      data=AutopaySerializer(
                                          autopay.first()).data,
                                      errors=[
                                          {
                                              "code": "SUBSCRIPTION_ALREADY_EXISTS",
                                              "message": "Subscription already exists"
                                          }
                                      ]))
    AutopayModel.objects.filter(
        user_id=user, status="CREATED", valid_till__gte=datetime.now()).delete()
    autopay = AutopayModel.objects.create(
        user_id=user,
        amount=150000,  # In paise
        startdate=datetime.now().date(),
        count=365,
    )
    payload = {
        "merchantSubscriptionId": autopay.subscription_id,
        "merchantUserId": user.user_id,
        "subscriptionName": "Filit Savings Subscription",
        "authWorkflowType": "PENNY_DROP",
        "amountType": "VARIABLE",
        "amount": 150000,
        "frequency": "DAILY",
        "recurringCount": 365,
        "description": "Max value that can be saved in a day",
        "mobileNumber": user.mobile
    }
    response = make_pay_request("/v3/recurring/subscription/create", payload)
    if response.status_code == 200:
        autopay.status = "CREATED"
        autopay.valid_till = datetime.fromtimestamp(
            float(response.json()["data"]["validUpto"])/1000, tz=None)
        autopay.phonepe_subscription_id = response.json()[
            "data"]["subscriptionId"]
        autopay.save()
        return Response(make_response("Subscription Initiated", data=AutopaySerializer(autopay).data))

    autopay.status = "FAILED"
    autopay.save()
    return Response(make_response("Subscription initiation failed", data=response.json(), status=400))


@api_view(["POST"])
def cancel_subscription(request):
    """
    DESCRIPTION
        This view will cancel a subscription for the given user.
    """
    user = request.user
    subscription = AutopayModel.objects.filter(user_id=user, status="ACTIVE")
    if not subscription.exists():
        return Response(make_response("Subscription doesn't exist",
                                      status=400,
                                      errors=[
                                          {
                                              "code": "SUBSCRIPTION_DOES_NOT_EXIST",
                                              "message": "Subscription doesn't exist, please make a new one"
                                          }
                                      ]))
    subscription = subscription.first()
    payload = {
        "merchantUserId": user.user_id,
        "subscriptionId": subscription.phonepe_subscription_id,
    }
    response = make_pay_request("/v3/recurring/subscription/cancel", payload)
    if response.status_code == 200:
        subscription.status = "CANCELLED"
        subscription.save()
        return Response(make_response("Subscription cancelled", data=response.json()["data"]))
    return Response(make_response("Subscription cancellation failed", errors=[
        {
            "code": response.json()["code"],
            "message":response.json()["message"]
        }
    ], status=400))


@api_view(["GET"])
def authorize_subscription(request):
    """
    DESCRIPTION
        This view will fetch an authorizing link for the given user.
    """
    user = request.user
    subscription = AutopayModel.objects.filter(user_id=user, status="CREATED").order_by('-valid_till')
    if not subscription.exists():
        return Response(make_response("Subscription doesn't exist",
                                      status=400,
                                      errors=[
                                          {
                                              "code": "SUBSCRIPTION_DOES_NOT_EXIST",
                                              "message": "Subscription doesn't exist, please make a new one"
                                          }
                                      ]))
    subscription = subscription.first()
    current_time = datetime.now(tz=None)
    validity = subscription.valid_till.replace(tzinfo=None)
    if validity < current_time:
        return Response(make_response("Subscription has expired",
                                      status=400,
                                      errors=[
                                          {
                                              "code": "SUBSCRIPTION_EXPIRED",
                                              "message": "Subscription has expired, please make a new one"
                                          }
                                      ]))

    auth = AuthRequest.objects.create(
        subscription=subscription
    )

    payload = {
        "merchantUserId": user.user_id,
        "subscriptionId": subscription.phonepe_subscription_id,
        "authRequestId": auth.auth_id,
    }
    response = make_pay_request("/v3/recurring/auth/init", payload,
                                callback="https://api.filit.in/payments/verify-subscription/")
    if response.status_code == 200:
        auth.status = True
        auth.save()
        return Response(make_response("Authorization link fetched", data=response.json()["data"]))
    return Response(make_response("Authorization link fetch failed", errors=[
        {
            "code": response.json()["code"],
            "message":response.json()["message"]
        }
    ], status=400))


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def verify_subscription(request):
    """
    DESCRIPTION
        This view will verify the subscription for the given user.
    """
    print("Callback received")
    try:
        if not check_checksum(request.headers["X-VERIFY"], request.data["response"]):
            print("Checksum failed")
            return Response("Invalid Checksum")
    except KeyError:
        return Response("Key Error")
    data = decipher_callback(request.data["response"])
    if data["code"] == "SUCCESS":
        data = data["data"]
        auth = AuthRequest.objects.filter(
            subscription_id=data["authRequestId"])
        subscription = auth.subscription
        if subscription.amount != data["amount"]:
            return Response("Invalid Transaction")
        subscription.status = "ACTIVE"
        return Response("Subscription Activated")
    return Response("Invalid Request")


@api_view(["GET"])
def check_subscription(request):
    """
    DESCRIPTION
        Status check for subscription
    """
    user = request.user
    subscription = AutopayModel.objects.filter(user_id=user, status="ACTIVE")
    if subscription.first():
        return Response(make_response("Subscription active", data=AutopaySerializer(subscription.first()).data))
    return Response("Subscription not active", status=400)


@api_view(["GET"])
def get_order_history(request):
    """
    DESCRIPTION
        Get all orders for the given user
    """
    user = request.user
    orders = TransactionDetails.objects.filter(
        user_id=user).order_by('-updated_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return Response(make_response("Orders fetched successfully", data={'items': TransactionSerializer(page_obj.object_list, many=True).data, 'has_next': page_obj.has_next()}))


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def verify_auto_debit(request):
    """
    DESCRIPTION
        This view will verify the debit request for the given user.
    """
    print("Debit callback received")
    try:
        if not check_checksum(request.headers["X-VERIFY"], request.data["response"]):
            print("Checksum failed")
            return Response("Invalid Checksum")
    except KeyError:
        return Response("Key Error")
    data = decipher_callback(request.data["response"])
    if data["code"] == "SUCCESS":
        data = data["data"]
        if (data["callbackType"] == "NOTIFY"):
            return Response("Notification failed")
        if (data["transactionDetails"]["state"] == "FAILED"):
            return Response("Payment Failed")
        txn = TransactionDetails.objects.filter(
            txn_id=data["merchantTransactionId"]).first()
        if (not txn):
            return Response("Invalid Transaction")
        if (txn.amount != data["amount"]):
            txn.completion_status = "FAILED"
            txn.save()
            return Response("Invalid Transaction")
        txn.completion_status = "SUCCESS"
        user = txn.user_id
        status, response = buy(user, txn)
        if status and response.status_code == 200:
            print("Payment Succeeded")
            txn.save()
            return Response("Payment Succeeded")
    print("Payment Failed")
    return Response("Payment Failed")
