import requests
from datetime import datetime
import os

from .models import GoldTokenModel

BASE_URL = "https://uat-api.augmontgold.com/api"
BASE_HEADERS = {
    "Content-Type": "application/json"
}


def get_token():
    """
    DESCRIPTION
        This function generates an access token for Augmont
    """
    curr_time = datetime.now(tz=None)
    token_model = GoldTokenModel.objects.first()
    if (not token_model):
        token_model = GoldTokenModel.objects.create()
    expiry = (token_model.expiry)
    expiry = expiry.replace(tzinfo=None)
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
        print("Will expire by", expiry_time.isoformat())
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
