import psycopg2
from psycopg2 import Error


import pandas as pd

from constants import PAYOUT_TABLE_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE


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
                address                 TEXT            PRIMARY KEY,
                scholar                 TEXT            NOT NULL,
                payout_address          TEXT            NOT NULL
          ); '''.format(PAYOUT_TABLE_NAME)

    cur.execute(create_table_query)
    conn.commit()

    cur.close()
    conn.close()


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = 'SELECT * FROM ' + PAYOUT_TABLE_NAME

    cur.execute(view_db)
    query_results = cur.fetchall()

    df = pd.DataFrame(query_results, columns=['address', 'scholar', 'payout_address'])
    return df


def get_scholar_payout_address(ronin_address):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = 'SELECT payout_address FROM {} WHERE address = \'{}\''.format(PAYOUT_TABLE_NAME, ronin_address.lower())

    cur.execute(view_db)
    query_results = cur.fetchall()

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

    cur.execute(add_row_query)
    conn.commit()

    cur.close()
    conn.close()


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

    cur.execute(add_entry_query)
    conn.commit()

    cur.close()
    conn.close()


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE address = '{}'".format(PAYOUT_TABLE_NAME, row[0]['ronin_address'])
    cur.execute(get_user_info_query)
    query_results = cur.fetchall()

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple addresses found with address {}: \n{}', row[0]['ronin_address'], query_results)

    conn.commit()
    cur.close()
    conn.close()
