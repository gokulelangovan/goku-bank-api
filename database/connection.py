import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn
