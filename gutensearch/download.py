"""
Downloads and saves a local copy of every English document
(in the form of a .txt) from Project Gutenberg in a simple,
and respectful way. Alternatively, the download can be
parameterized to limit the total number of documents downloaded.
"""
from typing import List

import requests
from bs4 import BeautifulSoup

def get_site_urls(url: str) -> List[str]:
    """
    Extract every `<a>` tag from the HTML of the
    given site, and return it as a list of strings.

    Parameters:
        url: The URL of the page

    Returns:
        Every link present from the page

    Raises:
        HTTPError: If there is an issue executing the request

    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text)
    links = [t.attrs.get('href') for t in soup.find_all('a')]
    
    return [l for l in links if l is not None]

def download_zip(url: str) -> str:
    ...