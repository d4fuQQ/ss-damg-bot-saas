import requests
import json
from web3.auto import w3
from eth_account.messages import encode_defunct

from constants import MAX_RETRIES, GRAPHQL_ENDPOINT

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',}


def get_raw_message():
    request_body = {"operationName":"CreateRandomMessage","variables":{},"query":"mutation CreateRandomMessage {\n  createRandomMessage\n}\n"}
    r = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, data=request_body)
    json_data = json.loads(r.text)
    return json_data['data']['createRandomMessage']


def get_sign_message(raw_message, account_private_key):
    private_key = bytearray.fromhex(account_private_key)
    message = encode_defunct(text=raw_message)
    hex_signature = w3.eth.account.sign_message(message, private_key=private_key)
    return hex_signature


def submit_signature(signed_message, message, ronin_address):
    request_body = {"operationName":"CreateAccessTokenWithSignature","variables":{"input":{"mainnet":"ronin","owner":"User's Eth Wallet Address","message":"User's Raw Message","signature":"User's Signed Message"}},"query":"mutation CreateAccessTokenWithSignature($input: SignatureInput!) {\n  createAccessTokenWithSignature(input: $input) {\n    newAccount\n    result\n    accessToken\n    __typename\n  }\n}\n"}
    request_body['variables']['input']['signature'] = signed_message['signature'].hex()
    request_body['variables']['input']['message'] = message
    request_body['variables']['input']['owner'] = ronin_address

    retries = MAX_RETRIES
    data_received = False

    while not data_received:
        response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=request_body)
        if response.status_code == 200:
            data_received = True
        else:
            print('Request failed.')
            retries -= 1
            if retries == 0:
                return False

    json_data = json.loads(response.text)

    # A failed request will look like this: {'errors': [{'message': 'TimeoutError: ResourceRequest timed out'}], 'data': None}
    if json_data['data'] is None:
        return False

    return json_data['data']['createAccessTokenWithSignature']['accessToken']
