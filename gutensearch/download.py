"""
Downloads and saves a local copy of every English document
(in the form of a .txt) from Project Gutenberg in a simple,
and respectful way. Alternatively, the download can be
parameterized to limit the total number of documents downloaded.
"""
import os
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Union, Sequence, Optional
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup # type: ignore

from .parse import parse_gutenberg_index

DATETIME_FMT = '%Y-%m-%d %H:%M:%S'

def save_metadata(meta: Dict[int, Dict[str, str]], path: Path) -> None:
    """
    Convenience function to save metadata to the given path

    Parameters:
        meta: The list of dictionaries containing the metadata
        path: The full path to save the data to
    """
    with open(path, 'w') as f:
        json.dump(meta, f, indent=2, default=str)

def save_document(doc: str, path: Path) -> None:
    """
    Convenience function to save the document to the given path

    Parameters:
        doc: The text document to save
        path: The full path name to save the document to
    """
    with open(path, 'w') as f:
        f.write(doc)

def document_url(id_: int) -> Optional[str]:
    """
    Generate the URL for the given document id,
    if one can be correctly inferred.

    Parameters:
        id_:
            The document id assigned by Project Gutenberg.
            See the [Gutenberg Index](https://www.gutenberg.org/dirs/GUTINDEX.ALL)
            for more information

    Returns:
        The URL string if it can be inferred, `None` otherwise
    """
    BASE_URL = 'https://aleph.gutenberg.org'

    prefix = str(id_)[:-1]
    if len(prefix) == 0:
        # don't know where to find single id docs (yet)
        return None
    return f"{BASE_URL}/{'/'.join(prefix)}/{id_}/"

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

def download_document_text(id_: int) -> Optional[str]:
    """
    Download the contents of the text file from the page
    for the provided document id. If more than one text
    files are found, the function will break ties in this order:

    - {id}.txt
    - {id}-0.txt
    - {id}-8.txt

    If no text files are found in the page, then
    the function will return `None`

    Parameters:
        id_:
            The document id assigned by Project Gutenberg.
            See the [Gutenberg Index](https://www.gutenberg.org/dirs/GUTINDEX.ALL)
            for more information

    Returns:
        The text, decoded from the .txt file if one is found,
        `None` if no .txt files are found otherwise.
    """
    url = document_url(id_)
    if url is None:
        return None

    files = get_site_urls(url)
    textfiles = [os.path.splitext(f)[0] for f in files if f.endswith('.txt')]
    textfiles = sorted(textfiles)

    if len(textfiles) == 0:
        return None

    # use the first item as the text to download
    time.sleep(1)
    url = f'{url}{textfiles[0]}.txt'
    response = requests.get(url)
    response.raise_for_status()

    return response.text

def download_gutenberg_documents(
    path: Path,
    limit: Optional[int] = None,
    delay: int = 2,
    only: Optional[List[int]] = None) -> None:
    """
    Utility function to download every .txt document from
    Project Gutenberg. This function supports incremental
    downloads by supplying an optional list of integers
    containing only specific id's of documents to download.

    Parameters:
        path:
            The directory to save the results. If it doesn't
            already exist, a new directory will be created.
        limit:
            Stop the download only after a given number of
            documents have been successfuly downloaded. Otherwise
            if `None`, continue downloading until all documents
            have been saved locally.
        delay:
            Delay execution of consecutive requests, in seconds
        only:
            List of document id's to exclusively download

    """
    log = logging.getLogger('gutensearch.download')

    # track download metadata such as url, datetime, path
    meta_path = path / '.meta.json'
    meta: Dict[int, Dict[str, str]] = {}

    # if the destination directory doesn't exist, create it
    if os.path.exists(path):
        # check for existing metadata and read it in first
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
    else:
        os.mkdir(path)

    # if a list of exclusive id's is provided use that
    if only is not None:
        ids = [i for i in only]
    else:
        # download the entire list first
        log.info('Downloading project gutenberg document index')
        time.sleep(1)
        ids = parse_gutenberg_index()

    # begin download each document
    counter: int = 0
    for i in ids:
        if limit is not None:
            if counter >= limit:
                log.info('Saving metadata and exiting')
                save_metadata(meta, meta_path)

        url = document_url(i)
        if url is None:
            log.info(f'Skipping document id: {i}')
            continue

        # wait between consecutive requests
        time.sleep(delay)
        text = download_document_text(i)
        if text is None:
            log.info(f'Skipping document id: {i}')
            continue

        # save the file contents
        filepath = path / f'{i}.txt'
        log.info(f'[{counter}/{limit}] Saving document to path: {filepath}')
        save_document(text, filepath)
        counter += 1

        # and record the metadata, indexing by document id
        meta[i] = {
            'url': url,
            'datetime': datetime.now().strftime(DATETIME_FMT),
            'filepath': str(filepath.resolve()),
        }

        # save metadata every 10 downloaded documents
        if counter % 10 == 0:
            log.info('Saving metadata checkpoint')
            save_metadata(meta, meta_path)
