import requests
from datetime import datetime, timedelta
import pytz
import os

from login.models import CustomUser
from gold.models import GoldHoldingsModel, GoldRatesModel, GoldTokenModel, GoldTransactionModel, GoldInvestorModel
from payments.models import TransactionDetails

BASE_URL = "https://uat-api.augmontgold.com/api"
BASE_HEADERS = {
    "Content-Type": "application/json"
}


def get_token():
    """
    DESCRIPTION
        This function generates an access token for Augmont
    """
    curr_time = datetime.now(tz=pytz.UTC)
    token_model = GoldTokenModel.objects.first()
    if (not token_model):
        token_model = GoldTokenModel.objects.create()
    expiry = (token_model.expiry)
    expiry = expiry.replace(tzinfo=pytz.UTC)
    if (expiry < curr_time):
        print("Getting new token")
        response = requests.post(BASE_URL + "/merchant/v1/auth/login",
                                 data={
                                     "email": os.getenv("AUGMONT_EMAIL"),
                                     "password": os.getenv("AUGMONT_PASS")
                                 }, timeout=5000)
        response = response.json()
        expiry_time = datetime.strptime(
            response["result"]["data"]["expiresAt"], "%Y-%m-%d %H:%M:%S")
        token_model.expiry = expiry_time
        token_model.token = response["result"]["data"]["accessToken"]
        token_model.token_type = response["result"]["data"]["tokenType"]
        token_model.save()
        print("Will expire by", expiry_time.isoformat(), "now is",
              curr_time.isoformat())
    return token_model.token_type + " " + token_model.token


def make_request(relative_url, body=None, headers=None, method="POST"):
    """
    DESCRIPTION
        This function will make a request to the given url.
    """
    auth = {"Authorization": get_token()}
    if not headers:
        headers = {}
    if not body:
        body = {}
    headers.update(BASE_HEADERS)
    headers.update(auth)
    if method == "GET":
        return requests.get(BASE_URL + relative_url, headers=headers, timeout=5000)
    if method == "POST":
        return requests.post(BASE_URL + relative_url, headers=headers, json=body, timeout=5000)
    if method == "PUT":
        return requests.put(BASE_URL + relative_url, headers=headers, json=body, timeout=5000)
    return requests.delete(BASE_URL + relative_url, headers=headers, timeout=5000)


def make_response(details="", data=None, status=200, errors=None):
    """
    DESCRIPTION
        This function will return the response in the required format.
    """
    ret: dict = {
        'statusCode': status,
    }
    if details:
        ret['message'] = details
    if data:
        ret['result'] = data
    if not errors:
        errors = []
    ret['errors'] = errors
    return ret


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
        rates.expiry = datetime.utcnow() + timedelta(minutes=2)
        rates.block_id = response["result"]["data"]["blockId"]
        rates.gold_buy = response["result"]["data"]["rates"]["gBuy"]
        rates.silver_buy = response["result"]["data"]["rates"]["sBuy"]
        rates.gold_sell = response["result"]["data"]["rates"]["gSell"]
        rates.silver_sell = response["result"]["data"]["rates"]["sSell"]
        rates.gold_buy_gst = response["result"]["data"]["rates"]["gBuyGst"]
        rates.silver_buy_gst = response["result"]["data"]["rates"]["sBuyGst"]
        rates.save()
    return rates


def buy(user: CustomUser, transaction: TransactionDetails):
    """
    Buy from Augmont
    """
    gold_user = GoldInvestorModel.objects.filter(user_id=user.user_id)
    if not gold_user:
        return False, "User not found"
    gold_user = gold_user.first()

    if not transaction.completion_status == "SUCCESS":
        return False, "Transaction not completed"

    rates = get_rates()
    is_autopay = True
    lock_price = rates.gold_buy

    gold_txn = GoldTransactionModel.objects.create(
        gold_user_id=gold_user,
        payment_id=transaction.payment_id,
        txn_type="buy",
        block_id=rates.block_id,
        lock_price=lock_price,
        metal_type="GOLD",
        amount=transaction.amount,
        is_autopay=is_autopay
    )
    payload = {
        "lockPrice": lock_price,
        "metalType": "GOLD",
        "amount": gold_txn.amount,
        "merchantTransactionId": gold_txn.gold_txn_id,
        "uniqueId": gold_user.gold_user_id,
        "blockId": rates.block_id
    }
    response = make_request("/merchant/v1/buy", body=payload)
    if (response.status_code == 200):
        holding, c = GoldHoldingsModel.objects.get_or_create(
            gold_user_id=gold_user)
        gold_txn.txn_id = response.json()["result"]["data"]["transactionId"]
        gold_txn.quantity = response.json()["result"]["data"]["quantity"]
        holding.gold_locked += response.json()["result"]["data"]["quantity"]
        gold_txn.status = "LOCKED"
        gold_txn.save()
        holding.save()
    return True, response
