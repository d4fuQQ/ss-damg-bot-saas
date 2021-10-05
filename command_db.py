import pandas as pd

from constants import DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE, COMMAND_TABLE_NAME
from db import connect, execute_query, execute_query_get_results


def create_table():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    create_table_query = '''CREATE TABLE IF NOT EXISTS {} (
                command                 TEXT         PRIMARY KEY,
                permissioned_role_ids   TEXT[]
          ); '''.format(COMMAND_TABLE_NAME)

    execute_query(create_table_query, cur, conn)


def get_entire_db():
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_table_query = 'SELECT * FROM ' + COMMAND_TABLE_NAME
    query_results = execute_query_get_results(view_table_query, cur, conn)
    df = pd.DataFrame(query_results, columns=['command', 'permissioned_role_ids'])
    return df


def get_command_line(command):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    view_table_query = "SELECT * FROM {} WHERE command='{}'".format(COMMAND_TABLE_NAME, command)
    query_results = execute_query_get_results(view_table_query, cur, conn)
    df = pd.DataFrame(query_results, columns=['command', 'permissioned_role_ids'])
    return df


def insert_row(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    add_row_query = '''
                INSERT INTO {} (command, permissioned_role_ids)
                VALUES ('{}', ARRAY{}::TEXT[])
          '''.format(COMMAND_TABLE_NAME, command, role_ids)

    execute_query(add_row_query, cur, conn)


def update_row(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)
    add_entry_query = '''
                    UPDATE {}
                    SET
                    permissioned_role_ids = ARRAY{}::TEXT[]
                    WHERE command = '{}'
              '''.format(COMMAND_TABLE_NAME, role_ids, command)

    execute_query(add_entry_query, cur, conn)


def update_db(command, role_ids):
    conn, cur = connect(DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE)

    get_user_info_query = "SELECT * FROM {} WHERE command = '{}'".format(COMMAND_TABLE_NAME, command)
    query_results = execute_query_get_results(get_user_info_query, cur, conn)

    if len(query_results) == 0:
        insert_row(command, role_ids)
    elif len(query_results) == 1:
        update_row(command, role_ids)
    else:
        raise Exception('Multiple commands called {} found: \n{}', command, query_results)
