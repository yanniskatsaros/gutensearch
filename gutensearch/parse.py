"""
This module contains functions for parsing a given document
by cleaning each word (removing punctuation & numbers and
converting to lower-case) and counting the unique occurence
of each word in the given document.
"""
import re
from typing import Sequence
from collections import Counter
from itertools import chain
from difflib import SequenceMatcher

NONLETTER_PATTERN = re.compile(r'[^a-zA-Z]')

def clean(s: str) -> str:
    """
    Removes any non-letter characters, and casts the
    entire string to lower case characters.

    Parameters:
        s: The string to clean

    Returns:
        An all-lower string with any non-letter characters removed
    """
    return re.sub(NONLETTER_PATTERN, '', s.strip().lower())

def parse_word_count(doc: str) -> Counter:
    """
    Count the occurence of each unique (cleaned) word from
    the provided text document.

    Parameters:
        lines: A sequence of lines containing text

    Returns:
        A counter where each key is a unique instance of a
        word, and the value is the count of how frequently
        that word occured in the given document.
    """
    # use lazy generator expressions, then only consume the stream once
    lines = (l.strip().split() for l in doc.strip().split('\n'))
    words = (clean(s) for s in chain(*lines))

    # the stream is only consumed once when counting each word
    return Counter(words)

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
