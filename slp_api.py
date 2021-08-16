import json

import requests
import bs4

from constants import LUNACIAROVER_ENDPOINT, HEADERS, MAX_RETRIES


# Retrieve updated on, last claim timestamp, claimed (total) slp, rank?, mmr, win rate
# Total is unclaimed + claimed, in_game_slp is unclaimed? and ronin is how much is in wallet
def get_slp_stats(ronin_address):
    url = LUNACIAROVER_ENDPOINT.format(ronin_address)

    retries = MAX_RETRIES
    data_received = False

    while not data_received:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data_received = True
        else:
            retries -= 1
            if retries == 0:
                raise Exception('SLP data retrieval failed for {}: Error: {}'.format(ronin_address, response.text))

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    info = json.loads(soup.find('p').getText())
    return info
