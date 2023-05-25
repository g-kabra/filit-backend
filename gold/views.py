from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

import pytz
from datetime import datetime, timedelta

from .models import GoldInvestorModel, GoldBankModel, GoldAddressModel, GoldRatesModel, GoldTransactionModel, GoldAutopayModel

from .functions import make_request

from .serializers import TransactionSerializer

# Create your views here.

#! User Related


@api_view(["POST"])
def register_user(request, *args, **kwargs):
    user = request.user
    if (not user.pincode or not user.first_name):
        return Response("Insufficient information", status=400)
    if(GoldInvestorModel.objects.get(user_id=user)):
        return Response("Already registered", status=400)
    mobileNumber = user.mobile
    userName = user.first_name + " " + user.last_name
    new_user = GoldInvestorModel.objects.create(user_id=user)
    uniqueId = new_user.gold_user_id
    payload = {
        "mobileNumber": mobileNumber,
        "userPincode": user.pincode,
        "userName": userName,
        "uniqueId": uniqueId
    }
    headers = {
        "Accept": "application/json"
    }
    response = make_request("/merchant/v1/users",
                            body=payload, headers=headers)
    return Response(response.json())


@api_view(["GET"])
def get_user(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id, method="GET").json())


@api_view(["POST"])
def set_nominee(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    response = make_request("/merchant/v1/users/"+gold_user.gold_user_id, body={
        "nomineeName": request.data.get("nominee_name"),
        "nomineeRelation": request.data.get("nominee_relation"),
        "nomineeDateOfBirth": request.data.get("nominee_dob"),
        "userName": user.first_name + " " + user.last_name,
        "userPincode": user.pincode,
    }, method="PUT")
    gold_user.nomineeName = request.data.get("nominee_name")
    gold_user.nomineeRelation = request.data.get("nominee_relation")
    gold_user.nomineeDateOfBirth = datetime.strptime(
        request.data.get("nominee_dob"), "%Y-%m-%d")
    gold_user.save()
    return Response(response.json())


@api_view(["POST"])
def register_bank(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    payload = {
        "accountNumber": request.data.get("account_number"),
        "accountName": request.data.get("account_name"),
        "ifscCode": request.data.get("ifsc_code")
    }
    response = make_request("/merchant/v1/users/" +
                            gold_user.gold_user_id+"/banks", body=payload)
    if(response.status_code >= 400):
        return Response(response.json())
    GoldBankModel.objects.create(
        gold_user_id=gold_user,
        bank_id=response["result"]["data"]["userBankId"],
        account_number=response["result"]["data"]["accountNumber"],
        account_name=response["result"]["data"]["accountName"],
        ifsc_code=response["result"]["data"]["ifscCode"]
    )
    return Response(response.json())


@api_view(["GET"])
def get_banks(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id+"/banks", method="GET").json())


@api_view(["DELETE"])
def delete_bank(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    bank_id = request.data.get("bank_id")
    GoldBankModel.objects.get(bank_id=bank_id).delete()
    return Response(make_request("/merchant/v1/users/"+gold_user.gold_user_id+"/banks/"+bank_id, method="DELETE").json())

# ? Bank Updation

# * Address Registration


@api_view(["POST"])
def register_address(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
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

# ? Address Updation

#! Investment Related

# * Get current rates


def get_rates():
    rates = GoldRatesModel.objects.first()
    if (not rates):
        rates = GoldRatesModel.objects.create()
    curr_time = datetime.now(pytz.utc)
    if (rates.expiry <= curr_time):
        response = make_request("/merchant/v1/rates", method="GET")
        response = response.json()
        rates.expiry = datetime.now() + timedelta(minutes=4)
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
def get_rates_view(request, *args, **kwargs):
    rates = get_rates()
    return Response({
        "gBuy": rates.gold_buy,
        "gSell": rates.gold_sell,
        "sBuy": rates.silver_buy,
        "sSell": rates.silver_sell,
        "gBuyGst": rates.gold_buy_gst,
        "sBuyGst": rates.silver_buy_gst
    })

@api_view(["POST"])
def buy(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    rates = get_rates()
    metalType = request.data.get("metal_type")
    amount = request.data.get("amount")
    lockPrice = rates.gold_buy
    if (metalType == "silver"):
        lockPrice = rates.silver_buy
    txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user,
        txn_type="buy",
        block_id=rates.block_id,
        lock_price=lockPrice,
        metal_type=metalType,
        amount=amount
    )
    payload = {
        "lockPrice": lockPrice,
        "metalType": metalType,
        "amount": amount,
        "merchantTransactionId": txn.gold_txn_id,
        "uniqueId": gold_user.gold_user_id,
        "blockId": rates.block_id
    }
    response = make_request("/merchant/v1/buy", body=payload)
    if (response.status_code == 200):
        txn.status = True
        txn.save()
    return Response(response.json())


@api_view(["POST"])
def sell(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    rates = get_rates()
    metalType = request.data.get("metal_type")
    amount = request.data.get("amount")
    bank_id = request.data.get("bank_id")
    lockPrice = rates.gold_sell
    if (metalType == "silver"):
        lockPrice = rates.silver_sell
    txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user,
        txn_type="sell",
        block_id=rates.block_id,
        lock_price=lockPrice,
        metal_type=metalType,
        amount=amount,
        bank_id=GoldBankModel.objects.get(bank_id=bank_id)
    )
    payload = {
        "lockPrice": lockPrice,
        "metalType": metalType,
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
        txn.status = True
        txn.save()
    return Response(response.json())


@api_view(["POST"])
def start_autopay(request, *args, **kwargs):
    user = request.user
    gold_user = GoldInvestorModel.objects.get(user_id=user.user_id)
    GoldAutopayModel.objects.create(
        gold_user=gold_user,
        autopay_amount=request.data.get("autopay_amount"),
        startdate=datetime.now().date()
    )
    return Response("Added Autopay")


# ? Place Redeem Order (Product details)

#! Information Related

class TransactionViewSet(viewsets.ModelViewSet):
    txn = GoldTransactionModel
    queryset = txn.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (AllowAny, )
    def get_gold_user(self):
        user = self.request.user
        gold_user = GoldInvestorModel.objects.get(user_id = user.user_id)
        return gold_user
    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_admin:
                return self.queryset
            return self.queryset.filter(gold_user_id=self.get_gold_user().gold_user_id)
        return None

# ? Withdraw Status

# ? Passbook

# ? Invoices
