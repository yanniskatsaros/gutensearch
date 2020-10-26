"""
This module provides functions to interface with the project
Postgres database, including inserting/loading data and
executing a variety of queries/searches.
"""
import os
from typing import Dict, Any, Iterable

import psycopg2
from psycopg2.extensions import connection # type: ignore

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

def dbconfig() -> Dict[str, str]:
    """
    psycopg2 database connection settings

    Returns:
        A dictionary with the following keys

        - `host`
        - `port`
        - `dbname`
        - `user`
        - `password`
    """
    return {
        'host': POSTGRES_HOST,
        'port': POSTGRES_PORT,
        'dbname': POSTGRES_DB,
        'user': POSTGRES_USER,
        'password': POSTGRES_PASSWORD,
    }

def insert_records(con: connection, table: str, records: Iterable[Dict[str, Any]]):
    """
    Generic utility function to insert records in the form of
    a sequence of dictionaries, where each key in the dictionary
    represents the column name in the specified table.

    Parameters:
        con: Connection to the Postgres database
        table: The name of the table to insert the records into
        records:
            A sequence (iterable) of dictionaries, where each
            dictionary is inserted as a single "row" in the table
    """
    # do nothing for empty records
    if len(records) == 0:
        return

    params = [f'%({c})s' for c in records[0].keys()]
    wildcards = f'({", ".join(params)})'

    # generate the SQL statement - doesn't actually bind any
    # external data apart from the table name provided by the caller
    sql = f"""
    INSERT INTO {table}
    VALUES {wildcards}
    """
    with con.cursor() as cur:
        cur.executemany(sql, records)

    con.commit()
