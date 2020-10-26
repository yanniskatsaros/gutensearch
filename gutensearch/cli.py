import os
import json
import logging
from pathlib import Path
from argparse import ArgumentParser, Namespace
from multiprocessing import cpu_count, Pool
from itertools import chain
from io import StringIO

import psycopg2  # type: ignore

from .download import download_gutenberg_documents
from .parse import parse_gutenberg_index, parse_document
from .database import insert_records, dbconfig

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

    # subparser for parsing/loading data into the db
    parser_load = subparser.add_parser(
        'load',
        help='Parse and load the word counts from documents into the gutensearch database',
    )
    parser_load.add_argument(
        '--path',
        help='The path to the directory containing the documents',
        default=Path('data'),
        type=Path,
    )
    parser_load.add_argument(
        '--limit',
        help='Only parse and load a limited number of documents',
        type=int,
        default=None,
    )
    parser_load.add_argument(
        '--multiprocessing',
        help='Perform the parse/load in parallel using multiple cores',
        action='store_true',
        default=False,
    )
    parser_load.add_argument(
        '--log-level',
        help='Set the level for the logger',
        choices=LOG_LEVEL_CHOICES.keys(),
        default='info',
    )
    parser_load.set_defaults(__load=True)

    return parser

def load_main(args: Namespace):
    """
    Entrypoint for the `gutensearch load` command
    """
    log = logging.getLogger('gutensearch.load')
    log.setLevel(LOG_LEVEL_CHOICES[args.log_level])

    files = [args.path/f for f in os.listdir(args.path) if f.endswith('.txt')]

    # parse/load only the first `n` files if --limit
    if args.limit is not None:
        files = files[:args.limit]

    # only use multiple cpu's if requested
    if args.multiprocessing:
        cpus = cpu_count()
        log.info(f'Parsing {len(files)} documents using {cpus} cores')

        with Pool(cpus) as p:
            records = chain(*p.map(parse_document, files))
    else:
        log.info(f'Parsing {len(files)} documents using 1 core')
        records = chain(*[parse_document(f) for f in files])

    # connect to the db and save the results
    with psycopg2.connect(**dbconfig()) as con:
        cur = con.cursor()

        log.info('Temporarily dropping indexes on table: words')
        sql = """
        DROP INDEX IF EXISTS idx_words_word;
        DROP INDEX IF EXISTS idx_words_id;
        """.strip()
        cur.execute(sql)

        log.info('Writing results to database')
        # create an in-memory file-stream to copy the data
        # using Postgres' high performance `COPY` command
        with StringIO() as fio:
            for d in records:
                text = '\t'.join(str(v) for v in d.values())
                fio.write(text + '\n')

            fio.seek(0)
            cur.copy_from(fio, 'words')
            log.info('Finished writing data to database')

        log.info('Recreating indexes on table: words')
        sql = """
        CREATE INDEX idx_words_word ON words (word);
        CREATE INDEX idx_words_id ON words(document_id);
        """.strip()
        cur.execute(sql)

        log.info('Committing changes to database')
        con.commit()
        cur.close()

        log.info('Running vacuum analyze on table: words')
        cur = con.cursor()
        iso_level = con.isolation_level
        con.set_isolation_level(0)
        cur.execute('VACUUM ANALYZE words')

        log.info('Committing changes to database')
        con.commit()
        con.set_isolation_level(iso_level)
        cur.close()

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

    if hasattr(args, '__load'):
        load_main(args)