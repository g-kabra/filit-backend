"""
Functions for the payment app
"""
import json
import os
import hashlib
import base64
import requests
from login.models import CustomUser

from payments.models import AutopayModel, TransactionDetails

BASE_URL = "https://api-preprod.phonepe.com/apis/pg-sandbox"
BASE_HEADERS = {
    "Content-Type": "application/json",
}


def make_pay_request(relative_url, body: dict = None, callback: str = None):
    """
    DESCRIPTION
        This function will make a request to the given url.
    """

    body["merchantId"] = os.getenv("PHONEPE_MERCHANT_ID")
    body: str = json.dumps(body)
    body_encoded = base64.b64encode(body.encode()).decode()
    base: str = body_encoded
    base += relative_url
    base += os.getenv("PHONEPE_SALT_KEY")
    base = base.encode()
    hash_object = hashlib.sha256()
    hash_object.update(base)
    x_verify = hash_object.hexdigest() + "###" + os.getenv("PHONEPE_SALT_INDEX")
    headers = {
        "X-VERIFY": x_verify
    }
    if callback:
        headers['X-CALLBACK-URL'] = callback
    headers.update(BASE_HEADERS)
    body = {
        "request": body_encoded
    }
    return requests.post(BASE_URL + relative_url, headers=headers, json=body, timeout=5000)


def make_debit_request(user: CustomUser, amount):
    """
    DESCRIPTION
        Uses subscription to make a debit request.
    """
    subscription = AutopayModel.objects.filter(user_id=user).first()
    if not subscription or subscription.status != "ACTIVE":
        return False
    txn = TransactionDetails.objects.create(
        user=user, amount=amount, txn_type="AUTOPAY")
    body = {
        "merchantUserId": user.user_id,
        "transactionId": txn.txn_id,
        "subscriptionId": subscription.subscription_id,
        "autoDebit": True,
        "amount": amount,
    }
    relative_url = "/v3/recurring/debit/init"
    callback = "https://api.filit.in/payments/callback-debit/"
    response = make_pay_request(relative_url, body, callback)
    return response.status_code < 300

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


def decipher_callback(data: str):
    """
    DESCRIPTION
        This function will decipher the callback data.
    """
    data = base64.b64decode(data)
    data = data.decode()
    data = json.loads(data)
    return data


def check_checksum(x_verify: str, data: str):
    """
    DESCRIPTION
        This function will check the checksum of the callback data.
    """
    [hash_value, salt_index] = x_verify.split("###")
    base: str = data + os.getenv("PHONEPE_SALT_KEY")
    base = base.encode()
    hash_object = hashlib.sha256()
    hash_object.update(base)
    x_verify_self = hash_object.hexdigest()
    return x_verify_self == hash_value
