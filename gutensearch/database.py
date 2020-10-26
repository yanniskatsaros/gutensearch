"""
This module provides functions to interface with the project
Postgres database, including inserting/loading data and
executing a variety of queries/searches.
"""
import os
from typing import Dict

import psycopg2

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