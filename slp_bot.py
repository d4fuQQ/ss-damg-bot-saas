import datetime
import time

from commands_bot import user_has_permission
from constants import TIMESTAMP_FORMAT, MIN_DAYS_FOR_INCLUSION, PLAYERS_IN_TOP_RANK_COMMAND, \
    SCHOLARS_TO_EXCLUDE_FROM_TOP_RANK, DEV_RONIN_ADDRESSES
from discord_helpers import send_message
from encryption import return_scholar_dict, get_address_to_discord_id_dict
from slp_api import get_slp_stats
from slp_db import update_db, get_entire_db


def run_update():
    scholar_data = return_scholar_dict()

    print('Updating DB....')
    for info in scholar_data.values():
        name = info[0]
        ronin_address = info[1]

        slp_stats = get_slp_stats(ronin_address)
        slp_stats['name'] = name

        update_db(slp_stats)

        print('User {} updated with address {}'.format(name, ronin_address))

        # Sleep to not annoy the API
        time.sleep(.5)


def convert_timestamp_to_seconds(series):
    return series.apply(lambda x: int(datetime.datetime.strptime(str(x), TIMESTAMP_FORMAT).strftime('%s')))


def get_days_since_last_claimed_series(last_claimed_series, last_updated_series):
    return (convert_timestamp_to_seconds(last_updated_series) - convert_timestamp_to_seconds(last_claimed_series)) \
           / 86400


def retrieve_info():
    db = get_entire_db()

    get_days_since_last_claimed_series(db['last_claimed'], db['last_updated'])
    db['average_slp'] = db['unclaimed_slp'] / get_days_since_last_claimed_series(db['last_claimed'], db['last_updated'])
    db = db.sort_values('average_slp', ascending=False)

    return db


def convert_number_to_ordinal(num):
    if num % 10 == 1:
        return str(num) + 'st'
    if num % 10 == 2:
        return str(num) + 'nd'
    if num % 10 == 3:
        return str(num) + 'rd'
    else:
        return str(num) + 'th'


async def get_individual_rank_msg(user, channel):
    scholar_dict = return_scholar_dict()

    if str(user.id) not in scholar_dict:
        await send_message("Hi <@{}>, your info has not yet been added to the bot by your manager.", user.id, user)
        return

    scholar_info = scholar_dict[str(user.id)]
    discord_name = scholar_info[0]
    ronin_address = scholar_info[1]

    df = retrieve_info()

    excluded_addresses = SCHOLARS_TO_EXCLUDE_FROM_TOP_RANK

    if ronin_address in excluded_addresses:
        row = df.loc[df['address'].str.match(ronin_address)]
        name = row['name'].iloc[0]
        avg_slp = row['average_slp'].iloc[0]

        msg = 'Hi, {}!\n'.format(name)
        msg += 'Your average SLP per day is {:.1f}\n'.format(avg_slp)

        await send_message(msg, user)
        return

    else:
        for addr in excluded_addresses:
            df = df.loc[df['address'] != addr]

    # This is the wrong way to do this, I should find their row by address and then find index
    rank = 1
    avg_slp = -1
    days_since_claimed = -1
    for row_id, row in df.iterrows():
        days_since_claimed = get_days_since_claimed(row['last_updated'], row['last_claimed'])
        if row['address'] == ronin_address:
            avg_slp = row['average_slp']
            break
        if days_since_claimed >= MIN_DAYS_FOR_INCLUSION:
            rank += 1

    if avg_slp == -1:
        raise Exception("Failed to retrieve info for {} at address {}".format(discord_name, ronin_address))

    msg = 'Hi, {}!\n'.format(discord_name)
    msg += 'Your average SLP per day is {:.1f}\n'.format(avg_slp)
    msg += 'You are currently in {} place!'.format(convert_number_to_ordinal(rank))

    if days_since_claimed < MIN_DAYS_FOR_INCLUSION:
        msg += '\nOnce your current cycle exceeds 5 days you\'ll be eligible for the leaderboard.'

    await send_message(msg, user)


def get_days_since_claimed(last_updated, last_claimed):
    last_updated = int(datetime.datetime.strptime(str(last_updated), TIMESTAMP_FORMAT).strftime('%s'))
    last_claimed = int(datetime.datetime.strptime(str(last_claimed), TIMESTAMP_FORMAT).strftime('%s'))

    return (last_updated - last_claimed) / 86400


async def get_top_rank_msg(user, channel, players_to_include=PLAYERS_IN_TOP_RANK_COMMAND, override=False):
    if not user_has_permission(user, "!rank top") and not override:
        return

    df = retrieve_info()

    excluded_addresses = SCHOLARS_TO_EXCLUDE_FROM_TOP_RANK

    for addr in excluded_addresses:
        df = df.loc[df['address'] != addr]

    if len(df.index) < players_to_include:
        return

    emoji_list = [':first_place:', ':second_place:', ':third_place:', ':moneybag:', ':crossed_swords:', ':rocket:',
                  ':money_with_wings:', ':gem:', ':pick:', ':eyes:']

    msg = 'Top {} highest daily avg SLP for the month as of {}:\n\n'.format(players_to_include,
                                                                            datetime.datetime.today().strftime(
                                                                                '%Y-%m-%d'))

    address_to_discord_id = get_address_to_discord_id_dict()

    count = 0
    for key, row in df.iterrows():
        days_since_claimed = get_days_since_claimed(row['last_updated'], row['last_claimed'])
        if days_since_claimed < MIN_DAYS_FOR_INCLUSION:
            continue

        if count == 3:
            msg += '------------------------------------\n'
        msg += '<@{}> : {:.1f} SLP AVG {}\n'.format(address_to_discord_id[row['address']],
                                                    row['average_slp'],
                                                    emoji_list[count] if count < len(emoji_list) else '')
        count += 1

        if count >= players_to_include:
            break

    if count < players_to_include:
        return

    await send_message(msg, channel)


async def get_all_rank_msg(user, channel):
    if not user_has_permission(user, "!rank all"):
        return

    df = retrieve_info()

    excluded_addresses = DEV_RONIN_ADDRESSES

    for addr in excluded_addresses:
        df = df.loc[df['address'] != addr]

    msg = 'All SLP Earners as of {}:\n\n'.format(datetime.datetime.today().strftime('%Y-%m-%d'))

    address_to_discord_id = get_address_to_discord_id_dict()

    for key, row in df.iterrows():
        days_since_claimed = get_days_since_claimed(row['last_updated'], row['last_claimed'])
        if days_since_claimed < 1:
            continue

        if row['address'] not in address_to_discord_id:
            continue

        msg += '<@{}> : {:.1f} SLP AVG\n'.format(address_to_discord_id[row['address']], row['average_slp'])

    await send_message(msg, channel)


if __name__ == "__main__":
    run_update()
