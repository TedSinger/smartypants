import os
from psycopg.rows import namedtuple_row
import psycopg


def get_db_connection():
    pgpass = os.getenv("PGPASSWORD")
    return psycopg.connect(
        "dbname=smartypants user=twilio",
        sslmode='require',
        host=os.getenv("PGHOST"),
        password=pgpass,
        port=5432
    )


def q(cursor, query, *args) -> [namedtuple_row]:
    cursor.execute(query, [args] if args else [])
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
