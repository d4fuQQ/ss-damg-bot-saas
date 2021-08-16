from constants import HEADERS, MAX_RETRIES, PVE_SLP_ENDPOINT, DEV_IDS

import json
import requests
import bs4
import time

from encryption import return_scholar_dict


def get_slp_stats(ronin_address):
    time.sleep(.25)
    url = PVE_SLP_ENDPOINT.format(ronin_address)

    retries = MAX_RETRIES
    data_received = False

    while not data_received:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data_received = True
        else:
            retries -= 1
            if retries == 0:
                raise Exception('PVE SLP data retrieval failed for {}: Error: {}'.format(ronin_address, response.text))

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    info = json.loads(soup.find('p').getText())
    return info


def get_daily_pve_summary():
    msg = ''

    players_to_finish = 0
    total_players = 0
    for discord_id, info in return_scholar_dict().items():
        address = info[1]

        if int(discord_id) not in DEV_IDS:
            total_players += 1
            gained_pve_slp = get_slp_stats(address)['gained_slp_response']['gained_slp']

            if gained_pve_slp < 50:
                players_to_finish += 1
                msg += '<@{}>: {} SLP\n'.format(discord_id, gained_pve_slp)

    msg = 'Daily PVE RSS Summary: ({} out of {} players still to finish)\n'.format(players_to_finish, total_players) \
          + msg

    return msg
