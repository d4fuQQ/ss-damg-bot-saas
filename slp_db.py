import datetime

import psycopg2
from psycopg2 import Error

import pandas as pd

from constants import SLP_TABLE_NAME, TIMESTAMP_FORMAT, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE


def connect(user, password, host, database):
    try:
        conn = psycopg2.connect(user=user,
                                password=password,
                                host=host,
                                port="5432",
                                database=database)

        cur = conn.cursor()
        return conn, cur

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)


# Create table (don't run again! Only here for safe keeping. Does not overwrite existing tables).
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
                win_percentage          NUMERIC         NOT NULL
          ); '''.format(SLP_TABLE_NAME)

    cur.execute(create_table_query)
    conn.commit()

    cur.close()
    conn.close()


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = 'SELECT * FROM ' + SLP_TABLE_NAME

    cur.execute(view_db)
    query_results = cur.fetchall()

    df = pd.DataFrame(query_results, columns=['address', 'name', 'unclaimed_slp', 'claimed_slp', 'last_claimed',
                                              'last_updated', 'mmr', 'total_matches', 'win_percentage'])
    return df


def insert_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row['ronin_address']
    name = row['name']
    unclaimed_slp = row['in_game_slp']
    claimed_slp = row['ronin_slp']
    last_claimed = datetime.datetime.fromtimestamp(row['last_claim_timestamp']).strftime(TIMESTAMP_FORMAT)
    last_updated = datetime.datetime.fromtimestamp(row['updated_on']).strftime(TIMESTAMP_FORMAT)
    mmr = row['mmr']
    total_matches = row['total_matches']
    win_percent = row['win_rate']

    add_row_query = '''
                INSERT INTO {} (
                address, name, unclaimed_slp, claimed_slp, last_claimed, last_updated, mmr, total_matches, 
                win_percentage)

                VALUES

                ('{}', '{}', {}, {}, '{}', '{}', {}, {}, {})
          '''.format(SLP_TABLE_NAME, address, name, unclaimed_slp, claimed_slp, last_claimed, last_updated, mmr,
                     total_matches, win_percent)

    cur.execute(add_row_query)
    conn.commit()

    cur.close()
    conn.close()


def update_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row['ronin_address']
    name = row['name']
    unclaimed_slp = row['in_game_slp']
    claimed_slp = row['ronin_slp']
    last_claimed = datetime.datetime.fromtimestamp(row['last_claim_timestamp']).strftime(TIMESTAMP_FORMAT)
    last_updated = datetime.datetime.fromtimestamp(row['updated_on']).strftime(TIMESTAMP_FORMAT)
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

    cur.execute(add_entry_query)
    conn.commit()

    cur.close()
    conn.close()


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE address = '{}'".format(SLP_TABLE_NAME, row['ronin_address'])
    cur.execute(get_user_info_query)
    query_results = cur.fetchall()

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple users found with id {}: \n{}', row['address'], query_results)

    conn.commit()
    cur.close()
    conn.close()
