import os
import logging
from pathlib import Path
from argparse import ArgumentParser

from .download import download_gutenberg_documents

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_URL = 'http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=en'
LOG_LEVEL_CHOICES = {
    'notset': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

def make_parser() -> ArgumentParser:
    """
    Argument parser factory for the `gutensearch` command-line-interface
    """
    parser = ArgumentParser(
        description='A searchable database for words and documents from Project Gutenberg'
    )
    subparser = parser.add_subparsers()

    # subparser for downloading data
    parser_download = subparser.add_parser(
        'download',
        help='Download documents in a safe and respectful way from Project Gutenberg'
    )
    parser_download.add_argument(
        '--url',
        help='The base URL to begin the download from',
        default=BASE_URL,
    )
    parser_download.add_argument(
        '--path',
        help='The path to the directory to store the documents',
        default=Path('data'),
        type=Path,
    )
    parser_download.add_argument(
        '--limit',
        help='Stop the download after a certain number of documents have been downloaded',
        type=int,
        default=None,
    )
    parser_download.add_argument(
        '--delay',
        help='Number of seconds to delay between requests',
        type=int,
        default=2,
    )
    parser_download.add_argument(
        '--log-level',
        help='Set the level for the logger',
        choices=LOG_LEVEL_CHOICES.keys(),
        default='info',
    )
    parser_download.set_defaults(__download=True)

    return parser

def main():
    """
    Entrypoint for the `gutensearch` command-line-interface
    """
    parser = make_parser()
    args = parser.parse_args()

    if hasattr(args, '__download'):
        logging.getLogger().setLevel(LOG_LEVEL_CHOICES[args.log_level])

        try:
            download_gutenberg_documents(
                url=args.url,
                path=args.path,
                limit=args.limit,
                delay=args.delay
            )
        except KeyboardInterrupt:
            return
