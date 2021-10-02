import psycopg2
from psycopg2 import Error


def execute_query(query: str, cur, conn):
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()


def execute_query_get_results(query: str, cur, conn):
    cur.execute(query)
    conn.commit()
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


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
