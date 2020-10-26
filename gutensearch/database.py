"""
This module provides functions to interface with the project
Postgres database, including inserting/loading data and
executing a variety of queries/searches.
"""
import os
from typing import Dict

import psycopg2  # type: ignore
from psycopg2.extensions import connection # type: ignore

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

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
