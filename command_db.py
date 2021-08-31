import psycopg2
from psycopg2 import Error

import pandas as pd

from constants import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE, COMMAND_TABLE_NAME


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
                command                 TEXT         PRIMARY KEY,
                permissioned_role_ids   TEXT[]
          ); '''.format(COMMAND_TABLE_NAME)

    cur.execute(create_table_query)
    conn.commit()

    cur.close()
    conn.close()


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = 'SELECT * FROM ' + COMMAND_TABLE_NAME

    cur.execute(view_db)
    query_results = cur.fetchall()

    df = pd.DataFrame(query_results, columns=['command', 'permissioned_role_ids'])
    return df


def get_command_line(command):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    view_db = "SELECT * FROM {} WHERE command='{}'".format(COMMAND_TABLE_NAME, command)

    cur.execute(view_db)
    query_results = cur.fetchall()

    df = pd.DataFrame(query_results, columns=['command', 'permissioned_role_ids'])
    return df


def insert_row(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    add_row_query = '''
                INSERT INTO {} (command, permissioned_role_ids)

                VALUES ('{}', ARRAY{}::TEXT[])
          '''.format(COMMAND_TABLE_NAME, command, role_ids)

    cur.execute(add_row_query)
    conn.commit()

    cur.close()
    conn.close()


def update_row(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    add_entry_query = '''
                    UPDATE {}
                    SET
                    permissioned_role_ids = ARRAY{}::TEXT[]
                    WHERE command = '{}'
              '''.format(COMMAND_TABLE_NAME, role_ids, command)

    cur.execute(add_entry_query)
    conn.commit()

    cur.close()
    conn.close()


def update_db(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE command = '{}'".format(COMMAND_TABLE_NAME, command)
    cur.execute(get_user_info_query)
    query_results = cur.fetchall()

    if len(query_results) == 0:
        insert_row(command, role_ids)
    elif len(query_results) == 1:
        update_row(command, role_ids)
    else:
        raise Exception('Multiple commands called {} found: \n{}', command, query_results)

    conn.commit()
    cur.close()
    conn.close()

