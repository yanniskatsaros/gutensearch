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

def search_word(word: str,
                limit: Optional[int] = None) -> List[NamedTuple]:
    """
    Searches the `gutensearch` database for every document with the given word
    and returns the results, ordered by the highest `count` for each document id.

    Parameters:
        word: The word to search for
        limit: Return only the records with the top `n` most frequent words

    Returns:
        A list of records where each record is an instance of a `NamedTuple`

    """
    sql = """
    SELECT word,
           document_id,
           count
      FROM words
     WHERE word = %s
     ORDER BY 3 DESC
    """.strip()
    return query(sql, params=(word, ), limit=limit)

def search_document(id_: int,
                    min_length: Optional[int] = None,
                    limit: Optional[int] = None) -> List[NamedTuple]:
    """
    Searches the `gutensearch` database for every word in the given document
    and returns the results, ordered by the highest `count` for each word.

    Parameters:
        id_: The document id to search for
        min_length: Exclude any words in the search with less than a minimum word length
        limit: Return only the records with the top `n` most frequent words

    Returns:
        A list of records where each record is an instance of a `NamedTuple`

    """
    if min_length is not None:
        sql = """
        SELECT word,
               document_id,
               count
          FROM words
         WHERE document_id = %s
           AND LENGTH(word) >= %s
         ORDER BY 3 DESC
        """.strip()
        return query(sql, params=(id_, min_length), limit=limit)
    
    sql = """
    SELECT word,
           document_id,
           count
      FROM words
     WHERE document_id = %s
     ORDER BY 3 DESC
    """.strip()
    return query(sql, params=(id_, ), limit=limit)
