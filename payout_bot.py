from commands_bot import user_has_permission
from discord_helpers import send_message
from encryption import return_scholar_dict, get_address_to_discord_id_dict
from helpers import is_valid_ronin_address
from payout_db import update_db, get_entire_db


async def run_update_payout(user, channel, payout_address):
    if not is_valid_ronin_address(payout_address):
        await send_message(
            'Hi, <@{}>. Input valid ronin or slp payout address as !payout your_address_here'.format(user.name),
            channel)
        return

    scholar_data = return_scholar_dict()

    info = []
    for key, value in scholar_data.items():
        if key == str(user.id):
            info.append({'ronin_address': value[1]})
            info.append({'scholar_name': value[0]})
            info.append({'payout_address': str(payout_address)})

    print('Updating DB....')
    update_db(info)
    print('{} updated payout address to: {}'.format(info[1]['scholar_name'], info[2]['payout_address']))

    msg = 'Hi, <@{}>. Your payout address was successfully updated!'.format(user.id)
    await send_message(msg, channel)


async def payout_pull(user, channel):
    scholar_data = return_scholar_dict()

    info = []
    for key, value in scholar_data.items():
        if key == str(user.id):
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

    await send_message(msg, channel)


async def payout_request_scholars(user, channel):
    if not user_has_permission(user, "!payout request"):
        return

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
    #excluded_address = '0x9a6d68b161d547924bd65691302f92ad2b463d8d'
    #address_to_discord_id.pop(excluded_address)

    for discord_id in address_to_discord_id.values():
        msg += '<@{}> : Payout Needed.\n'.format(discord_id)

    await send_message(msg, channel)
