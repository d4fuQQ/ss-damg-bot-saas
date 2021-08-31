import json

import requests

from constants import GRAPHQL_ENDPOINT, MAX_RETRIES, CRYPTO_API_ENDPOINT, CRYPTO_API_TOKEN


def get_crypto_price(ticker):
    retries = MAX_RETRIES
    data_received = False

    while not data_received:
        response = requests.post(f"{CRYPTO_API_ENDPOINT}{ticker}{CRYPTO_API_TOKEN}")

        if response.status_code == 200:
            data_received = True
        else:
            retries -= 1
            if retries == 0:
                raise Exception('Crypto price call failed: {}: {}', response.status_code, response.text)

    result = json.loads(response.text)

    price = result['USD']

    return float(price)
