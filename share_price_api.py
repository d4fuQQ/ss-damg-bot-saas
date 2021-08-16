import json

import requests

from constants import GRAPHQL_ENDPOINT, MAX_RETRIES, CRYPTO_API_ENDPOINT, CRYPTO_API_TOKEN

base_query = """
{{ 
    axies(
        sort: PriceAsc,
        auctionType: Sale,
        criteria:
        {{
            classes: [{}],
            pureness: [6],
            parts: {}
        }}
      ) 
    {{
        total
        results {{
            id
            auction {{
                currentPriceUSD
            }}
        }}
    }}
}}
"""


# Total is unclaimed + claimed, in_game_slp is unclaimed? and ronin is how much is in wallet
def get_matched_axie(classes: str, parts, num_low_price):
    retries = MAX_RETRIES
    data_received = False

    query = base_query.format(classes, json.dumps(parts))

    while not data_received:
        response = requests.post(GRAPHQL_ENDPOINT, json={'query': query})

        if response.status_code == 200:
            data_received = True
        else:
            retries -= 1
            if retries == 0:
                raise Exception('Graphql call failed: {}: {}', response.status_code, response.text)

    result = json.loads(response.text)

    axies = result['data']['axies']

    if axies['total'] < num_low_price:
        raise Exception('Not enough axies')

    return float(axies['results'][num_low_price - 1]['auction']['currentPriceUSD'])


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
