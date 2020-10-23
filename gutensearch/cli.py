import os
import json
import logging
from pathlib import Path
from argparse import ArgumentParser

from .download import download_gutenberg_documents
from .parse import parse_gutenberg_index

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# BASE_URL = 'http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=en'
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

    # the following options are mutually exclusive
    me_download_group = parser_download.add_mutually_exclusive_group()
    me_download_group.add_argument(
        '--only',
        help='Download only the document ids listed in the given file',
    )
    me_download_group.add_argument(
        '--exclude',
        help='Download all document ids except those listed in the given file',
    )
    me_download_group.add_argument(
        '--use-metadata',
        help='Use the .meta.json file to determine which documents to download',
        action='store_true',
        default=False,
    )

    return parser

def main():
    """
    Entrypoint for the `gutensearch` command-line-interface
    """
    parser = make_parser()
    args = parser.parse_args()

    if hasattr(args, '__download'):
        logging.getLogger().setLevel(LOG_LEVEL_CHOICES[args.log_level])

        ids = None
        if args.only is not None:
            with open(args.only, 'r') as f:
                ids = [int(i.strip()) for i in f.readlines()]

        if args.exclude is not None:
            with open(args.except_ids, 'r') as f:
                exclude = [int(i.strip()) for i in f.readlines()]
            ids = list(set(ids) - set(exclude))

        if args.use_metadata:
            with open(args.path / '.meta.json', 'r') as f:
                meta = json.load(f)

            ids = parse_gutenberg_index()
            ids = list(set(ids) - set(int(i) for i in meta.keys()))

        try:
            download_gutenberg_documents(
                path=args.path,
                limit=args.limit,
                delay=args.delay,
                only=ids
            )
        except KeyboardInterrupt:
            return
