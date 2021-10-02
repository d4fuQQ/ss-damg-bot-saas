import datetime
import pandas as pd

from constants import SLP_TABLE_NAME, TIMESTAMP_FORMAT, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE, DAYS_TO_TRACK_SLP
from db import execute_query, connect, execute_query_get_results


def create_table():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    create_table_query = '''CREATE TABLE IF NOT EXISTS {} (
                address                 TEXT         PRIMARY KEY,
                name                    TEXT            NOT NULL,
                unclaimed_slp           INTEGER         NOT NULL,
                claimed_slp             INTEGER         NOT NULL,
                last_claimed            TIMESTAMP       NOT NULL,
                last_updated            TIMESTAMP       NOT NULL,    
                mmr                     TEXT            NOT NULL,
                total_matches           INTEGER         NOT NULL,
                win_percentage          NUMERIC         NOT NULL,
                yesterday_slp           INTEGER,
                daily_slp               INTEGER[]
          ); '''.format(SLP_TABLE_NAME)

    execute_query(create_table_query, cur, conn)


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_table_query = 'SELECT * FROM ' + SLP_TABLE_NAME
    query_results = execute_query_get_results(view_table_query, cur, conn)

    df = pd.DataFrame(query_results, columns=['address', 'name', 'unclaimed_slp', 'claimed_slp', 'last_claimed',
                                              'last_updated', 'mmr', 'total_matches', 'win_percentage',
                                              'yesterday_slp', 'daily_slp'])
    return df


def get_row(address):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_row_query = "SELECT * FROM {} WHERE address = '{}'".format(SLP_TABLE_NAME, address)
    query_results = execute_query_get_results(view_row_query, cur, conn)

    df = pd.DataFrame(query_results, columns=['address', 'name', 'unclaimed_slp', 'claimed_slp', 'last_claimed',
                                              'last_updated', 'mmr', 'total_matches', 'win_percentage',
                                              'yesterday_slp', 'daily_slp'])
    return df


def insert_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row['ronin_address']
    name = row['name']
    unclaimed_slp = row['in_game_slp']
    claimed_slp = row['ronin_slp']
    last_claimed = datetime.datetime.fromtimestamp(row['last_claim']).strftime(TIMESTAMP_FORMAT)
    last_updated = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    mmr = row['mmr']
    total_matches = row['total_matches']
    win_percent = row['win_rate']
    yesterday_slp = -1
    daily_slp = []

    add_row_query = '''
                INSERT INTO {} (
                address, name, unclaimed_slp, claimed_slp, last_claimed, last_updated, mmr, total_matches, 
                win_percentage, yesterday_slp, daily_slp)

                VALUES

                ('{}', '{}', {}, {}, '{}', '{}', {}, {}, {}, {}, ARRAY{}::integer[])
          '''.format(SLP_TABLE_NAME, address, name, unclaimed_slp, claimed_slp, last_claimed, last_updated, mmr,
                     total_matches, win_percent, yesterday_slp, daily_slp)

    execute_query(add_row_query, cur, conn)


def update_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row['ronin_address']
    name = row['name']
    unclaimed_slp = row['in_game_slp']
    claimed_slp = row['ronin_slp']
    last_claimed = datetime.datetime.fromtimestamp(row['last_claim']).strftime(TIMESTAMP_FORMAT)
    last_updated = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    mmr = row['mmr']
    total_matches = row['total_matches']
    win_percent = row['win_rate']

    add_entry_query = '''
                    UPDATE {}
                    SET
                    name = '{}',
                    unclaimed_slp = {}, 
                    claimed_slp = {}, 
                    last_claimed = '{}',
                    last_updated = '{}',
                    mmr = {}, 
                    total_matches = {}, 
                    win_percentage = {}
                    WHERE address = '{}'
              '''.format(SLP_TABLE_NAME, name, unclaimed_slp, claimed_slp, last_claimed, last_updated, mmr,
                         total_matches, win_percent, address)

    execute_query(add_entry_query, cur, conn)


def update_daily_slp(address):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    row = get_row(address).iloc[0]
    yesterday_total_slp = row['yesterday_slp']
    today_total_slp = row['unclaimed_slp']
    today_slp = today_total_slp - yesterday_total_slp
    daily_slp = row['daily_slp']
    daily_slp.insert(0, today_slp)
    daily_slp = daily_slp[:DAYS_TO_TRACK_SLP]

    update_daily_slp_query = '''
                        UPDATE {}
                        SET
                        yesterday_slp = {},
                        daily_slp = ARRAY{}::integer[]
                        WHERE address = '{}'
                  '''.format(SLP_TABLE_NAME, today_total_slp, daily_slp, address)

    execute_query(update_daily_slp_query, cur, conn)


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    get_user_info_query = "SELECT * FROM {} WHERE address = '{}'".format(SLP_TABLE_NAME, row['ronin_address'])
    query_results = execute_query_get_results(get_user_info_query, cur, conn)

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple users found with id {}: \n{}', row['address'], query_results)
