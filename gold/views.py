"""
Contains the views for the Augmont integration for Filit
"""
from datetime import datetime, timedelta
from rest_framework import views, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from gold.models import GoldAddressModel, GoldBankModel, GoldInvestorModel, GoldRatesModel, GoldTransactionModel, GoldDailySavingsModel

from .functions import make_request, make_response
from .serializers import BankSerializer, TransactionSerializer


class UserViews(views.APIView):
    """
    DESCRIPTION
        Methods for processing login and getting user details
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """ 
        Register user for gold
        """
        user = request.user
        if (not user.pincode or not user.first_name):
            return Response(make_response(
                "User details incomplete",
                status=400,
                errors=[
                    {
                        "code": "INCOMPLETE_DATA",
                        "message": "User details incomplete"
                    }
                ]
            ))
        if (GoldInvestorModel.objects.filter(user_id=user)):
            return Response(make_response(
                "User already registered",
                status=400,
                errors=[
                    {
                        "code": "ALREADY_REGISTERED",
                        "message": "User already registered for gold"
                    }
                ]
            ))
        new_user = GoldInvestorModel.objects.create(user_id=user)
        payload = {
            "mobileNumber": user.mobile,
            "userPincode": user.pincode,
            "userName": user.first_name + " " + user.last_name,
            "uniqueId": new_user.gold_user_id
        }
        headers = {
            "Accept": "application/json",
        }
        response = make_request("/merchant/v1/users",
                                body=payload, headers=headers)
        if response.status_code >= 300:
            new_user.delete()
            return Response(response.json())
        return Response(response.json())

    def get(self, request):
        """
        Fetch the current user details from Augmont
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id, method="GET").json())


@api_view(["POST"])
def set_nominee(request):
    """
    Set nominee for the user
    """
    user = request.user
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return Response(make_response(
            "User not registered",
            status=400,
            errors=[
                {
                    "code": "USER_NOT_REGISTERED",
                    "message": "User not registered for gold"
                }
            ]
        ))
    gold_user = gold_user.first()
    payload = {
        "nomineeName": request.data.get("name"),
        "nomineeRelation": request.data.get("relation"),
        "nomineeDateOfBirth": request.data.get("dob"),
        "userName": user.first_name + " " + user.last_name,
        "userPincode": user.pincode,
    }
    response = make_request(
        "/merchant/v1/users/"+gold_user.gold_user_id, body=payload, method="PUT")
    if response.status_code >= 300:
        return Response(response.json())
    gold_user.nominee_name = payload["nomineeName"]
    gold_user.nominee_date_of_birth = payload["nomineeDateOfBirth"]
    gold_user.nominee_relation = payload["nomineeRelation"]
    gold_user.save()
    return Response(response.json())


class BankViews(views.APIView):
    """
    Deals with the bank details of the user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Add bank details for the user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        payload = {
            "accountNumber": request.data.get("account_number"),
            "accountName": request.data.get("account_name"),
            "ifscCode": request.data.get("ifsc_code"),
        }
        response = make_request(
            "/merchant/v1/users/" + gold_user.gold_user_id+"/banks", body=payload)
        if response.status_code >= 300:
            return Response(response)
        response = response.json()
        GoldBankModel.objects.create(
            gold_user_id=gold_user,
            bank_id=response["result"]["data"]["userBankId"],
            account_number=response["result"]["data"]["accountNumber"],
            account_name=response["result"]["data"]["accountName"],
            ifsc_code=response["result"]["data"]["ifscCode"]
        )
        return Response(response)

    def get(self, request):
        """
        Fetch the bank details of the user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id+"/banks", method="GET").json())

    def delete(self, request):
        """
        Delete the bank details of the user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        bank_id = request.data.get("user_bank_id")
        response = make_request(
            "/merchant/v1/users/"+gold_user.gold_user_id+"/banks/"+bank_id, method="DELETE")
        if response.status_code >= 300:
            return Response(response.json())
        GoldBankModel.objects.get(bank_id=bank_id).delete()
        return Response(response.json())

    def put(self, request):
        """
        Update the bank details of the user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        bank_id = request.data.get("user_bank_id")
        bank = GoldBankModel.objects.get(bank_id=bank_id)
        bank = BankSerializer(bank, data=request.data, partial=True)
        if bank.is_valid():
            response = make_request("/merchant/v1/users/"+gold_user.gold_user_id+"/banks/"+bank_id, body={
                "accountNumber": bank.validated_data["account_number"],
                "accountName": bank.validated_data["account_name"],
                "ifscCode": bank.validated_data["ifsc_code"],
            }, method="PUT")
            if response.status_code < 300:
                bank.save()
                return Response(response.json())
            return Response(response.json(), status=400)
        return Response(bank.errors, status=400)


class AddressViews(views.APIView):
    """
    Deals with the address details of the user
    """

    def get(self, request):
        """
        Get the address details of the user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id+"/address", method="GET").json())

    def post(self, request):
        """
        Register new address for user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        payload = {
            "name": request.data.get("name"),
            "address": request.data.get("address"),
            "pincode": request.data.get("pincode"),
            "mobileNumber": request.data.get("mobile"),
        }
        response = make_request("/merchant/v1/users/" +
                                gold_user.gold_user_id+"/address", body=payload)
        GoldAddressModel.objects.create(
            gold_user_id=gold_user.gold_user_id,
            address_id=response["result"]["data"]["userAddressId"],
            name=response["result"]["data"]["name"],
            address=response["result"]["data"]["address"],
            pincode=response["result"]["data"]["address"],
            mobile=response
        )
        return Response(response.json())

    def delete(self, request):
        """
        Delete an address for user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        address_id = request.data.get("address_id")
        response = make_request(
            "/merchant/v1/users/"+gold_user.gold_user_id+"/address/"+address_id, method="DELETE")
        if response.status_code >= 300:
            return Response(response.json())
        GoldAddressModel.objects.get(address_id=address_id).delete()
        return Response(response.json())


def get_rates():
    """
    Get latest updated rates from Augmont
    """
    rates = GoldRatesModel.objects.first()
    if not rates:
        rates = GoldRatesModel.objects.create()
    curr_time = datetime.utcnow()
    expiry = rates.expiry
    expiry = expiry.replace(tzinfo=None)
    if expiry <= curr_time:
        response = make_request("/merchant/v1/rates", method="GET")
        response = response.json()
        rates.expiry = datetime.utcnow() + timedelta(minutes=4)
        rates.block_id = response["result"]["data"]["blockId"]
        rates.gold_buy = response["result"]["data"]["rates"]["gBuy"]
        rates.silver_buy = response["result"]["data"]["rates"]["sBuy"]
        rates.gold_sell = response["result"]["data"]["rates"]["gSell"]
        rates.silver_sell = response["result"]["data"]["rates"]["sSell"]
        rates.gold_buy_gst = response["result"]["data"]["rates"]["gBuyGst"]
        rates.silver_buy_gst = response["result"]["data"]["rates"]["sBuyGst"]
        rates.save()
    return rates


@api_view(["GET"])
def get_rates_view(request):
    """
    API view for getting latest updated rates from Augmont
    """
    rates = get_rates()
    return Response(make_response("Rates fetched successfully", data={
        "gBuy": rates.gold_buy,
        "gSell": rates.gold_sell,
        "sBuy": rates.silver_buy,
        "sSell": rates.silver_sell,
        "gBuyGst": rates.gold_buy_gst,
        "sBuyGst": rates.silver_buy_gst
    }))


@api_view(["POST"])
def buy(request):
    """
    Buy from Augmont
    """
    user = request.user
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return Response(make_response(
            "User not registered",
            status=400,
            errors=[
                {
                    "code": "USER_NOT_REGISTERED",
                    "message": "User not registered for gold"
                }
            ]
        ))
    gold_user = gold_user.first()

    rates = get_rates()
    metal_type = request.data.get("metal_type")
    amount = request.data.get("amount")
    is_autopay = request.data.get("is_autopay")
    lock_price = rates.gold_buy
    if (metal_type == "silver"):
        lock_price = rates.silver_buy
    txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user,
        txn_type="buy",
        block_id=rates.block_id,
        lock_price=lock_price,
        metal_type=metal_type,
        amount=amount,
        is_autopay=is_autopay
    )
    payload = {
        "lockPrice": lock_price,
        "metalType": metal_type,
        "amount": amount,
        "merchantTransactionId": txn.gold_txn_id,
        "uniqueId": gold_user.gold_user_id,
        "blockId": rates.block_id
    }
    response = make_request("/merchant/v1/buy", body=payload)
    if (response.status_code == 200):
        txn.txn_id = response.json()["result"]["data"]["transactionId"]
        txn.status = True
        txn.save()
    return Response(response.json())


@api_view(["POST"])
def sell(request):
    """
    Sell to Augmont
    """
    user = request.user
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return Response(make_response(
            "User not registered",
            status=400,
            errors=[
                {
                    "code": "USER_NOT_REGISTERED",
                    "message": "User not registered for gold"
                }
            ]
        ))
    gold_user = gold_user.first()

    rates = get_rates()
    metal_type = request.data.get("metal_type")
    amount = request.data.get("amount")
    bank_id = request.data.get("bank_id")
    lock_price = rates.gold_sell
    if (metal_type == "silver"):
        lock_price = rates.silver_sell
    if not GoldBankModel.objects.filter(bank_id=bank_id):
        return Response(make_response(
            "Invalid bank ID",
            status=400,
            errors=[
                {
                    "code": "BANK_NOT_REGISTERED",
                    "message": "Bank not registered, please recheck"
                }
            ]
        ))
    txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user,
        txn_type="sell",
        block_id=rates.block_id,
        lock_price=lock_price,
        metal_type=metal_type,
        amount=amount,
        bank_id=GoldBankModel.objects.get(bank_id=bank_id)
    )
    payload = {
        "lockPrice": lock_price,
        "metalType": metal_type,
        "amount": amount,
        "merchantTransactionId": txn.gold_txn_id,
        "uniqueId": gold_user.gold_user_id,
        "blockId": rates.block_id,
        "userBank": {
            "userBankId": bank_id
        }
    }
    response = make_request("/merchant/v1/sell", body=payload)
    if (response.status_code == 200):
        txn.txn_id = response.json()["result"]["data"]["transactionId"]
        txn.status = True
        txn.save()
    return Response(response.json())


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Viewset for transactions
    """
    txn = GoldTransactionModel
    queryset = txn.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (AllowAny, )

    def get_gold_user(self):
        """
        Get current user
        """
        user = self.request.user
        gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
        return gold_user

    def get_queryset(self):
        """
        Ensure restricted access to transactions
        """
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return self.queryset
            return self.queryset.filter(gold_user_id=self.get_gold_user().gold_user_id)
        return None


@api_view(["GET"])
def get_passbook(request):
    """
    Get passbook for a user
    """
    user = request.user
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return Response(make_response(
            "User not registered",
            status=400,
            errors=[
                {
                    "code": "USER_NOT_REGISTERED",
                    "message": "User not registered for gold"
                }
            ]
        ))
    gold_user = gold_user.first()

    response = make_request("/merchant/v1/users/" +
                            gold_user.gold_user_id+"/passbook", method="GET")
    return Response(response.json())


@api_view(["GET"])
def get_invoice(request):
    """
    Get invoice for a transaction
    """
    user = request.user
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return Response(make_response(
            "User not registered",
            status=400,
            errors=[
                {
                    "code": "USER_NOT_REGISTERED",
                    "message": "User not registered for gold"
                }
            ]
        ))
    gold_user = gold_user.first()
    txn_id = request.data.get("txn_id")
    response = make_request("/merchant/v1/invoice/" + txn_id, method="GET")
    return Response(response.json())


class DailySavingsViews(views.APIView):
    """
    Daily savings related views
    """
    def post(self, request):
        """
        Start daily savings for a user
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        startdate = datetime.utcnow().date()
        amount = request.data.get("amount")
        
        #? Discontinue previous
        daily_savings = GoldDailySavingsModel.objects.filter(gold_user=gold_user).first()
        if daily_savings:
            daily_savings.is_active = False
            daily_savings.save()

        daily_savings = GoldDailySavingsModel.objects.create(
            gold_user=gold_user,
            dailysavings_amount=amount,
            startdate=startdate
        )
        return Response(make_response("Daily savings started successfully", data={
            "dailysavings_amount": daily_savings.dailysavings_amount,
            "start_date": daily_savings.startdate
        }))
    
    def get(self, request):
        """
        Get daily savings items
        """
        user = request.user
        gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
        if not gold_user:
            return Response(make_response(
                "User not registered",
                status=400,
                errors=[
                    {
                        "code": "USER_NOT_REGISTERED",
                        "message": "User not registered for gold"
                    }
                ]
            ))
        gold_user = gold_user.first()
        daily_savings = GoldDailySavingsModel.objects.filter(gold_user=gold_user).first()
        if not daily_savings:
            return Response(make_response(
                "Daily savings not started",
                status=400,
                errors=[
                    {
                        "code": "DAILY_SAVINGS_NOT_STARTED",
                        "message": "Daily savings not started for user"
                    }
                ]
            ))
        return Response(make_response("Daily savings fetched successfully", data={
            "dailysavings_amount": daily_savings.dailysavings_amount,
            "start_date": daily_savings.startdate,
            "processed": daily_savings.processed,
            "is_active": daily_savings.is_active
        }))

