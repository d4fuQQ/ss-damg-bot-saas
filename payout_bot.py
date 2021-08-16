from encryption import return_scholar_dict, get_address_to_discord_id_dict
from payout_db import update_db, get_entire_db


def run_update_payout(discord_id, payout_address):
    scholar_data = return_scholar_dict()

    info = []
    for key, value in scholar_data.items():
        if key == str(discord_id):
            info.append({'ronin_address': value[1]})
            info.append({'scholar_name': value[0]})
            info.append({'payout_address': str(payout_address)})

    print('Updating DB....')
    update_db(info)
    print('{} updated payout address to: {}'.format(info[1]['scholar_name'], info[2]['payout_address']))


def payout_pull(discord_id):
    scholar_data = return_scholar_dict()

    info = []
    for key, value in scholar_data.items():
        if key == str(discord_id):
            info.append({'ronin_address': value[1]})
            info.append({'scholar_name': value[0]})

    print('Retrieving Payout Information: {}....'.format(info[1]['scholar_name']))
    df = get_entire_db()

    row = df.loc[df['address'].str.match(info[0]['ronin_address'])]
    if len(row):
        payout_address = row['payout_address'].iloc[0]

        msg = 'Hi, {}!\n'.format(info[1]['scholar_name'])
        msg += 'Payout is: {}'.format(payout_address)

    else:
        msg = 'Hi, {}!\n'.format(info[1]['scholar_name'])
        msg += 'You do not have a payout address set'

    return msg


def payout_request_scholars():
    df = get_entire_db()
    address_to_discord_id = get_address_to_discord_id_dict()

    msg = 'All Players Input Payout Address !payout.\n\n'

    info = []
    for key, row in df.iterrows():
        info.append(row['address'])

    for scholar in info:
        if scholar in address_to_discord_id:
            address_to_discord_id.pop(scholar)

    # Remove Dev Address
    excluded_address = '0x9a6d68b161d547924bd65691302f92ad2b463d8d'
    address_to_discord_id.pop(excluded_address)

    for discord_id in address_to_discord_id.values():
        msg += '<@{}> : Payout Needed.\n'.format(discord_id)

    return msg
