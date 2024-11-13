import os
from typing import List
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool


_POOL = []


def get_pool():
    if not _POOL:
        _POOL.append(ConnectionPool(
            conninfo=f"postgresql://twilio:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}:5432",
            kwargs={
                'sslmode': "require",
                'dbname': "smartypants"
            },
            open=True
        ))
    return _POOL[0]


def get_db_connection():
    p = get_pool()
    p.check()
    return p.connection()


def q(cursor, query, *args) -> List[namedtuple_row]:
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
