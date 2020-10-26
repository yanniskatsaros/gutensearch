"""
This module provides functions to interface with the project
Postgres database, including inserting/loading data and
executing a variety of queries/searches.
"""
import os
from typing import Dict, List, NamedTuple, Tuple, Any, Optional

import psycopg2                               # type: ignore
from psycopg2.extensions import connection    # type: ignore
from psycopg2.extras import NamedTupleCursor  # type: ignore

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

def query(sql: str, params: Optional[Tuple[Any]] = None, limit: Optional[int] = None) -> List[NamedTuple]:
    """
    Convenience function to easily execute a read-only query
    from the database and return the results.

    Parameters:
        sql: The SQL query to execute
        params: Data to bind to parameters in the query
        limit: Return only the first `n` records from the result

    Returns:
        A list of records where each record is an instance of a `NamedTuple`

    """
    with psycopg2.connect(**dbconfig()) as con:
        cur = con.cursor(cursor_factory=NamedTupleCursor)

        # auto-cleanup if there is an error
        try:
            cur.execute(sql, params)
        except Exception as e:
            cur.close()
            raise(e)
        
        if limit is not None:
            results = cur.fetchmany(limit)
        else:
            results = cur.fetchall()
        
        cur.close()

    return results
