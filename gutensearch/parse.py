import re

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
