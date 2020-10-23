"""
Downloads and saves a local copy of every English document
(in the form of a .txt) from Project Gutenberg in a simple,
and respectful way. Alternatively, the download can be
parameterized to limit the total number of documents downloaded.
"""
import os
from typing import List, Dict, Union, Sequence
from io import BytesIO
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup # type: ignore

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

    soup = BeautifulSoup(response.text, features='html.parser')
    links = [t.attrs.get('href') for t in soup.find_all('a')]
    
    return [l for l in links if l is not None]

def download_zip_text(url: str) -> List[Dict[str, Union[str, Sequence[str]]]]:
    """
    Download and parse the contents of all text files
    from the given URL string of a zip file, stripping
    any leading/trailing whitespace from each line of each file.

    Parameters:
        url: The URL string of the zip file

    Returns:
        A list of dictionaries, where each dictionary contains
        the id of the document, and the lines parsed as utf-8 strings.

    """
    response = requests.get(url)
    response.raise_for_status()

    # open the zip file
    zfile = ZipFile(BytesIO(response.content))
    # and only keep any docs with .txt attachments
    txt_files = [f for f in zfile.namelist() if f.endswith('.txt')]

    contents = []
    for file in txt_files:
        # first get the file name (needed for the document id)
        name, _ = os.path.splitext(file)

        # then open and parse the file contents as UTF-8 strings
        with zfile.open(file) as f:
            lines = [l.decode('utf-8').strip() for l in f.readlines()]
            contents.append({
                'id': name,
                'lines': lines,
            })

    return contents
