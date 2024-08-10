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


def q(cursor, query, *args):
    cursor.execute(query, [args] if args else [])
    cursor.row_factory = namedtuple_row
    return cursor.fetchall()
