import pandas as pd

from constants import PAYOUT_TABLE_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE
from db import connect, execute_query, execute_query_get_results


def create_table():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    create_table_query = '''CREATE TABLE IF NOT EXISTS {} (
                address                 TEXT            PRIMARY KEY,
                scholar                 TEXT            NOT NULL,
                payout_address          TEXT            NOT NULL
          ); '''.format(PAYOUT_TABLE_NAME)

    execute_query(create_table_query, cur, conn)


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_table_query = 'SELECT * FROM ' + PAYOUT_TABLE_NAME

    query_results = execute_query_get_results(view_table_query, cur, conn)

    df = pd.DataFrame(query_results, columns=['address', 'scholar', 'payout_address'])
    return df


def get_scholar_payout_address(ronin_address):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_table_query = 'SELECT payout_address FROM {} WHERE address = \'{}\''.format(PAYOUT_TABLE_NAME, ronin_address.lower())
    query_results = execute_query_get_results(view_table_query, cur, conn)

    if len(query_results) == 0:
        return None

    if len(query_results) > 1:
        raise Exception("More than 1 address found")

    payout_addr = query_results[0][0]

    return payout_addr


def insert_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row[0]['ronin_address']
    scholar = row[1]['scholar_name']
    payout_address = row[2]['payout_address']

    add_row_query = '''
                INSERT INTO {} (
                address, scholar, payout_address)
                VALUES
                ('{}', '{}', '{}')
          '''.format(PAYOUT_TABLE_NAME, address, scholar, payout_address)

    execute_query(add_row_query, cur, conn)


def update_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    address = row[0]['ronin_address']
    scholar = row[1]['scholar_name']
    payout_address = row[2]['payout_address']

    add_entry_query = '''
                    UPDATE {}
                    SET
                    scholar = '{}',
                    payout_address = '{}'
                    WHERE address = '{}'
              '''.format(PAYOUT_TABLE_NAME, scholar, payout_address, address)

    execute_query(add_entry_query, cur, conn)


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE address = '{}'".format(PAYOUT_TABLE_NAME, row[0]['ronin_address'])
    query_results = execute_query_get_results(get_user_info_query, cur, conn)

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple addresses found with address {}: \n{}', row[0]['ronin_address'], query_results)
