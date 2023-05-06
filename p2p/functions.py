import requests

BASE_URL = "https://api-dev.lendbox.in/v1/partners"
BASE_HEADERS = {"x_api_key": "",
                "x_api_code": ""}


def make_request(relative_url, body={}, headers={}, method="POST"):
    headers.update(BASE_HEADERS)
    if method == 'GET':
        return requests.get(BASE_URL + relative_url, headers=headers)
    elif method == 'POST':
        return requests.post(BASE_URL + relative_url, headers=headers, data=body)
