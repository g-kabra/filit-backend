from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model

import pytz
from datetime import datetime, timedelta

from .models import GoldInvestorModel, GoldBankModel, GoldAddressModel, GoldRatesModel, GoldTransactionModel

from .functions import make_request

# Create your views here.

#! User Related

# * Registration


@api_view(["POST"])
def register_user(request, *args, **kwargs):
    user = request.user
    if (not user.pincode or not user.first_name):
        return Response("Insufficient information", status=400)
    userPincode = user.pincode
    mobileNumber = user.mobile
    userName = user.first_name + " " + user.last_name
    new_user = GoldInvestorModel.objects.create(user_id=user)
    uniqueId = new_user.gold_user_id
    payload = {
        "mobileNumber": mobileNumber,
        "userPincode": userPincode,
        "userName": userName,
        "uniqueId": uniqueId
    }
    headers = {
        "Accept": "application/json"
    }
    response = make_request("/merchant/v1/users",
                            body=payload, headers=headers)
    return Response(response.json())

# ? Updation
# @api_view(["PUT"])
# def update_gold_user(request, *args, **kwargs):

# * Bank Registration


@api_view(["POST"])
def register_bank(request, *args, **kwargs):
    user = request.user
    gold_user_id = GoldInvestorModel.objects.get(
        gold_user_id=user.gold_user_id)
    payload = {
        "accountNumber": request.data.get("account_number"),
        "accountName": request.data.get("account_name"),
        "ifscCode": request.data.get("ifsc_code")
    }
    response = make_request("/merchant/v1/users/" +
                            gold_user_id+"/banks", body=payload)
    response = response.json()
    GoldBankModel.objects.create(
        gold_user_id=gold_user_id,
        bank_id=response["result"]["data"]["userBankId"],
        account_number=response["result"]["data"]["accountNumber"],
        account_name=response["result"]["data"]["accountName"],
        ifsc_code=response["result"]["data"]["ifscCode"]
    )
    return response

# ? Bank Updation

# * Address Registration


@api_view(["POST"])
def register_address(request, *args, **kwargs):
    user = request.user
    gold_user_id = GoldInvestorModel.objects.get(
        gold_user_id=user.gold_user_id)
    payload = {
        "name": request.data.get("name"),
        "address": request.data.get("address"),
        "pincode": request.data.get("pincode"),
        "mobileNumber": request.data.get("mobile"),
    }
    response = make_request("/merchant/v1/users/" +
                            gold_user_id+"/address", body=payload)
    response = response.json()
    GoldAddressModel.objects.create(
        gold_user_id=gold_user_id,
        address_id=response["result"]["data"]["userAddressId"],
        name=response["result"]["data"]["name"],
        address=response["result"]["data"]["address"],
        pincode=response["result"]["data"]["address"],
        mobile=response
    )
    return response

# ? Address Updation

#! Investment Related

# * Get current rates


def get_rates():
    rates = GoldRatesModel.objects.first()
    if(not rates):
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

# * Place Buy Order


@api_view(["POST"])
def buy(request, *args, **kwargs):
    user = request.user
    gold_user_id = GoldInvestorModel.objects.get(
        gold_user_id=user.gold_user_id)
    rates = get_rates()
    metalType = request.data.get("metal_type")
    lockPrice = rates.gold_buy
    if (metalType == "silver"):
        lockPrice = rates.silver_buy
    txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user_id,
        txn_type="buy",
        block_id=rates.blockId,
        lock_price=lockPrice,
        metal_type=metalType,
        amount=request.data.get("amount")
    )
    payload = {
        "lockPrice": lockPrice,
        "metalType": metalType,
        "amount": request.data.get("amount"),
        "merchantTransactionId": txn.gold_txn_id,
        "uniqueId": gold_user_id.gold_user_id,
        "blockId": rates.blockId
    }
    response = make_request("/merchant/v1/buy", body=payload)
    if(response.status_code == 200):
        txn.status = True
        txn.save()
    return response

# ? Place Sell Order

# @api_view(["GET"])
# def sell(request, *args, **kwargs):
#     user = request.user
    

# ? Place Redeem Order (Product details)

#! Information Related

# ? Withdraw Status

# ? Passbook

# ? Invoices
