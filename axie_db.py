import pandas as pd

from constants import AXIE_TABLE_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE


from db import connect, execute_query_get_results, execute_query


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

    execute_query(create_table_query, cur, conn)


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_table_query = 'SELECT * FROM ' + AXIE_TABLE_NAME
    query_results = execute_query_get_results(view_table_query, cur, conn)
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

    execute_query(add_row_query, cur, conn)


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

    execute_query(add_entry_query, cur, conn)


def update_db(row):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE axie_id = '{}'".format(AXIE_TABLE_NAME, row['id'])
    query_results = execute_query_get_results(get_user_info_query, cur, conn)

    if len(query_results) == 0:
        insert_row(row)
    elif len(query_results) == 1:
        update_row(row)
    else:
        raise Exception('Multiple axies found with id {}: \n{}', row['axie_id'], query_results)
