import os
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
