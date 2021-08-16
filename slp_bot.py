import datetime
import time

from constants import TIMESTAMP_FORMAT, MIN_DAYS_FOR_INCLUSION
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


def get_individual_rank_msg(ronin_address):
    df = retrieve_info()

    # This is the wrong way to do this, I should find their row by address and then find index
    rank = 1
    avg_slp = -1
    name = ''
    days_since_claimed = -1
    for row_id, row in df.iterrows():
        days_since_claimed = get_days_since_claimed(row['last_updated'], row['last_claimed'])
        if row['address'] == ronin_address:
            avg_slp = row['average_slp']
            name = row['name']
            break
        if days_since_claimed >= MIN_DAYS_FOR_INCLUSION:
            rank += 1

    if avg_slp == -1:
        return False

    msg = 'Hi, {}!\n'.format(name)
    msg += 'Your average SLP per day is {:.1f}\n'.format(avg_slp)
    msg += 'You are currently in {} place!'.format(convert_number_to_ordinal(rank))

    if days_since_claimed < MIN_DAYS_FOR_INCLUSION:
        msg += '\nOnce your current cycle exceeds 5 days you\'ll be eligible for the leaderboard.'

    return msg


def get_days_since_claimed(last_updated, last_claimed):
    last_updated = int(datetime.datetime.strptime(str(last_updated), TIMESTAMP_FORMAT).strftime('%s'))
    last_claimed = int(datetime.datetime.strptime(str(last_claimed), TIMESTAMP_FORMAT).strftime('%s'))

    return (last_updated - last_claimed) / 86400


def get_top_rank_msg():
    players_to_include = 10

    df = retrieve_info()

    if len(df.index) < players_to_include:
        return False

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
        return False

    return msg


def get_all_rank_msg():
    df = retrieve_info()

    msg = 'All SLP Earners as of {}:\n\n'.format(datetime.datetime.today().strftime('%Y-%m-%d'))

    address_to_discord_id = get_address_to_discord_id_dict()

    for key, row in df.iterrows():
        days_since_claimed = get_days_since_claimed(row['last_updated'], row['last_claimed'])
        if days_since_claimed < MIN_DAYS_FOR_INCLUSION:
            continue

        if row['address'] not in address_to_discord_id:
            continue

        msg += '<@{}> : {:.1f} SLP AVG\n'.format(address_to_discord_id[row['address']], row['average_slp'])

    return msg


if __name__ == "__main__":
    run_update()
