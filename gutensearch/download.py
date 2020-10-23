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

DATETIME_FMT = '%Y-%m-%d %H:%M:%S'

ENCODINGS = (
    'utf-8',
    'latin-1',
    'ascii',
)

def save_metadata(meta: List[Dict[str, str]], path: Path) -> None:
    """
    Convenience function to save metadata to the given path

    Parameters:
        meta: The list of dictionaries containing the metadata
        path: The full path to save the data to
    """
    with open(path, 'w') as f:
        json.dump(meta, f, indent=2, default=str)

def decode_bytes(b: bytes) -> Optional[str]:
    """
    Convenience function to attempt to decode bytes into a string

    Parameters:
        b:
            The bytes to attempt to decode. Options attempted:
            
            - `utf-8`
            - `latin-1`
            - `ascii`

    Returns:
        The bytes as a string if the decoding was succesful. `None` otherwise.
    """
    for enc in ENCODINGS:
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass

    return None

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

def download_zip_text(url: str) -> List[Dict[str, str]]:
    """
    Download and parse the contents of all text files
    from the given URL string of a zip file, and return
    a list of dictionaries containing the id and text of
    each document.

    Parameters:
        url: The URL string of the zip file

    Returns:
        A list of dictionaries, where each dictionary contains
        the id of the document, and the text parsed as a utf-8 string

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
        # make sure to parse the name in case it has any /
        name = Path(name.lower()).name

        with zfile.open(file) as f:
            # skip this file if it can't be decoded
            text = decode_bytes(f.read())
            if text is None:
                continue

            contents.append({
                'id': name,
                'text': text,
            })

    return contents

def download_gutenberg_documents(
    url: str,
    path: Path,
    limit: Optional[int] = None,
    delay: int = 2) -> None:
    """
    Utility function to download every .txt document from
    the given base URL, and save each result to the specified
    directory. Optionally, limit the total number of files
    downloaded, and modify the delay between consecutive requests.

    Parameters:
        url: The base URL from which to begin the download
        path: The path to the directory where to save the results
        limit: Stop the download after a given number of documents
        delay: Execute requests every `delay` __seconds__

    """
    log = logging.getLogger('gutensearch.download')

    # if the destination directory doesn't exist, create it
    if not os.path.exists(path):
        os.mkdir(path)

    # save metadata about the download for debugging/future reference
    meta: List[Dict[str, str]] = []
    meta_path = path / '.meta.json'

    # tracks the total number of files downloaded
    counter = 0

    while True:
        # begin by getting the first page of links
        links = get_site_urls(url)
        log.debug(f'Base url links from: {url}')
        if len(links) == 0:
            log.info('Saving metadata and exiting')
            save_metadata(meta, meta_path)
            return

        # we _assume_ the last link contains a url "pointer"
        # to the next page of links of interest
        final_link = links.pop(-1)
        log.debug(f'Last link from list: {final_link}')
        if final_link.endswith('.zip'):
            log.info('Saving metadata and exiting')
            save_metadata(meta, meta_path)
            return

        # however, it's only the query, not the absolute url
        # so we must construct it ourselves each time
        url_parts = urlsplit(url)
        url_query = urlsplit(final_link).query

        # construct the next url in a safe way
        next_url = urlunsplit((
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_query,
            ''
        ))

        for link in links:
            # skip any non-zip files that may pop up
            if not link.endswith('.zip'):
                log.info(f'Skipping url: {link}')
                continue

            # delay fast, consecutive requests to avoid getting banned :P
            time.sleep(delay)
            doc = download_zip_text(link)
            log.info(f'Downloading zip file contents from: {link}')

            # there may be multiple text files extracted
            for d in doc:
                file = path / Path(d['id'] + '.txt')
                log.info(f'({counter}/{limit}) Saving text file to: {file}')
                with open(file, 'w') as f:
                    f.write(d['text'])

                # increment for each document saved
                counter += 1

                # save metadata as well
                meta.append({
                    'url': link,
                    'id': d['id'],
                    'datetime_retrieved': datetime.now().strftime(DATETIME_FMT),
                    'path': str(file.resolve()),
                })

                if limit is not None:
                    if counter >= limit:
                        # save any outstanding metadata and break
                        log.info('Saving metadata and exiting')
                        save_metadata(meta, meta_path)
                        return

                # re-save the file every 10 downloads
                if counter % 10 == 0:
                    log.info('Saving metadata checkpoint')
                    save_metadata(meta, meta_path)

        # begin downloading from the next page
        log.debug(f'Next base url: {next_url}')
        url = next_url
