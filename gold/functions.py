import requests
from datetime import datetime
import pytz
import os

from .models import GoldTokenModel

BASE_URL = "https://uat-api.augmontgold.com/api"
BASE_HEADERS = {
    "Content-Type": "application/json"
}


def get_token():
    curr_time = datetime.now(pytz.utc)
    timezone = pytz.timezone('Asia/Kolkata')
    curr_time = timezone.localize(curr_time)
    token_model = GoldTokenModel.objects.first()
    if(not token_model):
        token_model = GoldTokenModel.objects.create()
    if (token_model.expiry <= curr_time):
        print("Getting new token")
        response = requests.post(BASE_URL + "/merchant/v1/auth/login",
                                 data={
                                     "email": os.getenv("AUGMONT_EMAIL"),
                                     "password": os.getenv("AUGMONT_PASS")
                                 })
        response = response.json()
        token_model.expiry = datetime.strptime(
            response["result"]["data"]["expiresAt"], "%Y-%m-%d %H:%M:%S")
        token_model.token = response["result"]["data"]["accessToken"]
        token_model.token_type = response["result"]["data"]["tokenType"]
        token_model.save()
    return token_model.token_type + " " + token_model.token


def make_request(relative_url, body={}, headers={}, method="POST"):
    auth = {"Authorization": get_token()}
    headers.update(BASE_HEADERS)
    headers.update(auth)
    if method == "GET":
        return requests.get(BASE_URL + relative_url, headers=headers)
    elif method == "POST":
        return requests.post(BASE_URL + relative_url, headers=headers, json=body)
    elif method == "PUT":
        return requests.put(BASE_URL + relative_url, headers=headers, json=body)
    elif method == "DELETE":
        return requests.delete(BASE_URL + relative_url, headers=headers)