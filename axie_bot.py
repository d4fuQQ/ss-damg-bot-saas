import time

from axie_api import get_axie_info
from axie_db import update_db
from encryption import return_scholar_dict


def run_update():
    scholar_data = return_scholar_dict()
    keys_to_remove = []
    for key, value in scholar_data.items():
        if value[-1] == 'mike':
            keys_to_remove.append(key)

    for key in keys_to_remove:
        scholar_data.pop(key)

    print('Updating DB....')
    for scholar_info in scholar_data.values():
        scholar = scholar_info[0]
        ronin_address = scholar_info[1]

        axie_info = get_axie_info(ronin_address)
        available_axies = axie_info['available_axies']['results']

        for axie in available_axies:
            if not axie['parts']:
                egg_dict = {'id': 'egg'}
                axie['parts'].append(egg_dict)
                axie['parts'].append(egg_dict)
                axie['parts'].append(egg_dict)
                axie['parts'].append(egg_dict)
                axie['parts'].append(egg_dict)
                axie['parts'].append(egg_dict)
                # print('Axie {} is still an egg'.format(axie['id']))
                axie['scholar_name'] = scholar
                axie['ronin_address'] = ronin_address
                update_db(axie)
                print('Axie {} updated with address {}'.format(axie['id'], ronin_address))
            else:
                axie['scholar_name'] = scholar
                axie['ronin_address'] = ronin_address
                update_db(axie)
                print('Axie {} updated with address {}'.format(axie['id'], ronin_address))

            # Sleep to not annoy the API
            time.sleep(.5)
