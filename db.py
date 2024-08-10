import os
from psycopg.rows import namedtuple_row
import psycopg
from psycopg_pool import ConnectionPool


from main import pool

def get_db_connection():
    return pool.getconn()


def q(cursor, query, *args) -> [namedtuple_row]:
    cursor.execute(query, args)
    cursor.row_factory = namedtuple_row
    return cursor.fetchall()


def q_one(cursor, query, *args) -> namedtuple_row:
    res = q(cursor, query, *args)
    if len(res) == 1:
        return res[0]
    elif not res:
        raise ValueError("No matching records")
    else:
        raise ValueError("Multiple matching records")
