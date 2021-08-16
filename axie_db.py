import psycopg2
from psycopg2 import Error


import pandas as pd

from constants import AXIE_TABLE_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE


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
                axie_id                 TEXT         PRIMARY KEY,
                axie_class              TEXT            NOT NULL,
                breed_count             INTEGER         NOT NULL,
                eyes                    TEXT            NOT NULL,
                ears                    TEXT            NOT NULL,
                back                    TEXT            NOT NULL,
                mouth                   TEXT            NOT NULL,
                horn                    TEXT            NOT NULL,
                tail                    TEXT            NOT NULL,
                scholar                 TEXT            NOT NULL,
                address                 TEXT            NOT NULL
          ); '''.format(AXIE_TABLE_NAME)

    cur.execute(create_table_query)
    conn.commit()

    cur.close()
    conn.close()


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = 'SELECT * FROM ' + AXIE_TABLE_NAME

    cur.execute(view_db)
    query_results = cur.fetchall()

    df = pd.DataFrame(query_results, columns=['axie_id', 'axie_class', 'breed_count', 'eyes', 'ears', 'back', 'mouth',
                                              'horn', 'tail', 'scholar', 'address'])
    return df


def insert_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    axie_id = row['id']
    axie_class = row['class']
    breed_count = row['breedCount']
    eyes = row['parts'][0]['id']
    ears = row['parts'][1]['id']
    back = row['parts'][2]['id']
    mouth = row['parts'][3]['id']
    horn = row['parts'][4]['id']
    tail = row['parts'][5]['id']
    scholar = row['scholar_name']
    address = row['ronin_address']

    add_row_query = '''
                INSERT INTO {} (
                axie_id, axie_class, breed_count, eyes, ears, back, mouth, horn, tail, scholar, address)

                VALUES

                ('{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
          '''.format(AXIE_TABLE_NAME, axie_id, axie_class, breed_count, eyes, ears, back, mouth, horn, tail, scholar,
                     address)

    cur.execute(add_row_query)
    conn.commit()

    cur.close()
    conn.close()


def update_row(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    axie_id = row['id']
    axie_class = row['class']
    breed_count = row['breedCount']
    eyes = row['parts'][0]['id']
    ears = row['parts'][1]['id']
    back = row['parts'][2]['id']
    mouth = row['parts'][3]['id']
    horn = row['parts'][4]['id']
    tail = row['parts'][5]['id']
    scholar = row['scholar_name']
    address = row['ronin_address']

    add_entry_query = '''
                    UPDATE {}
                    SET
                    axie_class = '{}', 
                    breed_count = {},
                    eyes = '{}',
                    ears = '{}',
                    back = '{}',
                    mouth = '{}',
                    horn = '{}',
                    tail = '{}', 
                    scholar = '{}',
                    address = '{}'
                    WHERE axie_id = '{}'
              '''.format(AXIE_TABLE_NAME, axie_class, breed_count, eyes, ears, back, mouth, horn, tail,
                         scholar, address, axie_id)

    cur.execute(add_entry_query)
    conn.commit()

    cur.close()
    conn.close()


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE axie_id = '{}'".format(AXIE_TABLE_NAME, row['id'])
    cur.execute(get_user_info_query)
    query_results = cur.fetchall()

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple axies found with id {}: \n{}', row['axie_id'], query_results)

    conn.commit()
    cur.close()
    conn.close()
