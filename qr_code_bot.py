import os
import uuid

import discord
import qrcode
import requests
import json
from web3.auto import w3
from eth_account.messages import encode_defunct

from commands_bot import user_has_permission
from constants import MAX_RETRIES, GRAPHQL_ENDPOINT
from discord_helpers import send_message
from encryption import return_scholar_dict

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


async def qr_bot(message, msg_pieces):
    scholar_dict = return_scholar_dict()
    if str(message.author.id) in scholar_dict:
        scholar_info = scholar_dict[str(message.author.id)]
        account_private_key = scholar_info[2]
        account_address = scholar_info[1]

        raw_message = get_raw_message()
        signed_message = get_sign_message(raw_message, account_private_key)
        access_token = submit_signature(signed_message, raw_message, account_address)

        if not access_token:
            msg = "Hi <@{}>, The QR bot is having trouble right now. Feel free to try again in a few" \
                  " seconds. If that doesn't work, we suggest logging in with your username and " \
                  "password.".format(message.author.id)
            await send_message(msg, message.author)
            return

        qr_code_path = f"QRCode_{message.author.id}_{str(uuid.uuid4())[0:8]}.png"
        qrcode.make(access_token).save(qr_code_path)

        await send_message("Hi <@{}>, here is your new QR Code to login".format(message.author.id), message.author)
        await message.author.send(file=discord.File(qr_code_path))

        os.remove(qr_code_path)
        return
    else:
        await send_message("Hi <@{}>, your account isn't yet set up to work with the QR code, but you can "
                           "still login in with username and password right now."
                           .format(message.author.id), message.author)
        return
