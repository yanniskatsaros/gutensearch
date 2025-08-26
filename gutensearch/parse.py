"""
This module contains functions for parsing a given document
by cleaning each word (removing punctuation & numbers and
converting to lower-case) and counting the unique occurence
of each word in the given document.
"""

import os
from typing import Sequence, List, IO, Generator, Dict, Union
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


def lazytokenize(io: IO) -> Generator[str, None, None]:
    """
    Apply a simple tokenization strategy to the stream
    of text provided by keeping any sequences of characters
    that are either lower/upper case letters. Any other
    characters (such as numbers, punctuation, whitespace)
    are discarded, and the "token buffer" is reset. This
    function is lazy and returns a generator object rather
    than building up the entire token sequence in memory.

    Parameters:
        io: The stream of text to tokenize

    Returns:
        A list of strings representing each "token"
    """
    # holds the current word being buffered
    chars: List[str] = []

    for line in io:
        for c in line:
            dec = ord(c)
            # keep only upper/lower chars
            isupper = 65 <= dec <= 90
            islower = 97 <= dec <= 122

            if isupper or islower:
                chars.append(c.lower())
            else:
                # save the word and flush
                if len(chars) > 0:
                    word = "".join(chars)
                    yield word

                chars = []


def parse_word_count(path: Path) -> Counter:
    """
    Count the occurence of each unique (cleaned & tokenized)
    word from the provided text document.
    This function is suitable to be used with multiprocessing.

    Parameters:
        path: The path to the document

    Returns:
        A counter where each key is a unique instance of a
        word, and the value is the count of how frequently
        that word occured in the given document.
    """
    with open(path, "r") as f:
        count = Counter(lazytokenize(f))

    return count


def parse_document(path: Path) -> List[Dict[str, Union[str, int]]]:
    """
    Parse the contents of the document from the given path and
    return the results as a dictionary with the document id
    and a dictionary of the unique word instances and their count.
    The function assumes that the name of the file contains the
    document id. For example, `18546.txt` would represent the
    document with id `18546`.

    This function is suitable to be used with multiprocessing.

    Parameters:
        path: The path to the document

    Returns:
        A list of dictionaries, where each dictionary represents
        a "record" of data with the keys `word`, `document_id`,
        and `count`.

    """
    id_ = path.name.split(".")[0]
    count = dict(parse_word_count(path))

    return [{"word": w, "document_id": id_, "count": c} for w, c in count.items()]


def closest_match(word: str, corpus: Sequence[str]) -> str:
    """
    Returns the word in the corpus that is the closest match
    to the word specified using the highest comparison "ratio".

    !!! warning
        This function will resolve ties simply by returning
        the first occurence of the highest ratio.

    Parameters:
        word: The word to perform a "fuzzy match" on
        corpus: The corpus of words to try and match against
    """
    ratios = [(w, SequenceMatcher(None, word, w).ratio()) for w in corpus]
    result = max(ratios, key=lambda x: x[1])

    return result[0]


def parse_gutenberg_index() -> List[int]:
    """
    Makes the best attempt at extracting each document id
    using the "Gutenberg Index" document which contains an
    id for each document in the entire database provided by
    Project Gutenberg.

    See: http://www.gutenberg.org/dirs/GUTINDEX.ALL

    Returns:
        A list of integers representing each document id

    """
    INDEX_URL = "http://www.gutenberg.org/dirs/GUTINDEX.ALL"
    PARENT = Path(__file__).parent.resolve()
    GUTENBERG_INDEX = PARENT / "gutenberg-index.txt"

    # attempt to read the index from a local file copy first
    if os.path.exists(GUTENBERG_INDEX):
        with open(GUTENBERG_INDEX, "r") as f:
            return [int(i) for i in f.read().strip().split("\n")]

    # delay import because we don't need it until now
    import requests

    response = requests.get(INDEX_URL)
    response.raise_for_status()

    text = response.content.decode("utf-8")
    lines = text.strip().split("\n")

    ids: List[int] = []
    for line in lines:
        parts = line.strip().split()

        # skip empty lines
        if len(parts) == 0:
            continue

        # we want the integer id at the end of each
        # document name line
        try:
            id_ = int(parts[-1])
        except ValueError:
            continue

        # do we want this in the future?
        # name = ' '.join(parts[0:-1])
        ids.append(id_)

    # drop any possible duplicates
    return list(set(ids))
