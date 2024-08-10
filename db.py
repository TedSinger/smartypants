import os
from psycopg.rows import namedtuple_row
import psycopg
from psycopg_pool import ConnectionPool

# Initialize connection pool
pgpass = os.getenv("PGPASSWORD")

_POOL = []
def get_pool():
    if not _POOL:
        _POOL.append(ConnectionPool(
            conninfo="dbname=smartypants user=twilio password={pgpass} host={os.getenv('PGHOST')} port=5432 sslmode=require"
        ))
    return _POOL[0]


def get_db_connection():
    return get_pool().getconn()


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
