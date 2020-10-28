# `gutensearch` :mag: :books:
A searchable database and command-line-interface for words and documents from Project Gutenberg

## Table of Contents

- [Installation](#installation)
    - [Alternative Installation](#alternative-installation)
- [Usage](#usage)
    - [`gutensearch download`](#gutensearch-download)
        - [Logging, Error Handling, and Metadata](#logging-error-handling-and-metadata)
    - [`gutensearch load`](#gutensearch-load)
    - [`gutensearch word`](#gutensearch-word)
    - [`gutensearch doc`](#gutensearch-doc)
- [Troubleshooting](#troubleshooting)
- [Discussion and Technical Details](#discussion-and-technical-details)
    - [Design](#design)
    - [Document ID](#document-id)
    - [Parsing Strategy](#parsing-strategy)
    - [Database Design](#database-design)
    - [Database Loading Strategy](#database-loading-strategy)
    - [Fuzzy Word Matching](#fuzzy-word-matching)
- [Benchmarks](#benchmarks)
    - [Parsing](#parsing)
    - [Loading](#loading)
    - [Word Search](#word-search)
    - [Document Search](#document-search)
- [Future Work](#future-work)

## Installation

The simplest way to install and run the project is using `docker` and `docker-compose`. To get started, in this directory (containing the `docker-compose.yml` file) run (or `docker-compose up --build -d` to run in detached mode)

- `docker-compose up --build`

This will build and start three services. The first is an empty Postgres database that has been initialized with the correct schema, and the second is the project documentation. Head over to `localhost:8000` on your browser to check them out! The third build is the project command-line-interface. 

Once Docker compose has finished setting up, you can run the container with the command-line-interface installed using the following command. When specifying the volume to mount, this assumes you have kept the example `data/` directory one level above this directory.

- `docker-compose run -v "$(pwd)/../data:/data" cli`

then load the documents into the database using

- `gutensearch load --path data/ --multiprocessing`

The example data provided has 1000 documents that are ready to be parsed and loaded. Depending on how many documents you are working with, you _may or may not_ need to tune the memory limits in the `docker-compose.yml` file prior to bringing the services up.

After this step has completed, you should see something similiar to this output

```
2020-10-28 01:46:11 [INFO] gutensearch.load - Parsing 1000 documents using 6 cores
2020-10-28 01:46:58 [INFO] gutensearch.load - Temporarily dropping indexes on table: words
2020-10-28 01:46:58 [INFO] gutensearch.load - Writing results to database
2020-10-28 01:47:36 [INFO] gutensearch.load - Finished writing data to database
2020-10-28 01:47:36 [INFO] gutensearch.load - Truncating table: distinct_words
2020-10-28 01:47:36 [INFO] gutensearch.load - Writing new distinct words to database
2020-10-28 01:47:49 [INFO] gutensearch.load - Finished writing distinct words to database
2020-10-28 01:47:49 [INFO] gutensearch.load - Recreating indexes on table: words
2020-10-28 01:48:04 [INFO] gutensearch.load - Committing changes to database
2020-10-28 01:48:04 [INFO] gutensearch.load - Running vacuum analyze on table: words
2020-10-28 01:48:05 [INFO] gutensearch.load - Committing changes to database
```

Your `gutensearch` cli is now setup and ready to be used! Head over to the [usage](#usage) section on information on how to get started and what commands are available.

For more information on this command, see the [`gutensearch load`](#load) section below. If you run into any issues during installation & setup, please see the [troubleshooting](#troubleshooting) section below.

### Alternative Installation

Alternatively, for a more "lightweight" installation where only the Postgres database is containerized, run

- `docker build -t db -f db.Dockerfile .`

to build and tag the Postgres image. To start the database, run

- `docker run -d --rm --name db -p 5432:5432 --shm-size=1g -e "POSTGRES_DB=postgres" -e "POSTGRES_PASSWORD=postgres" -e "POSTGRES_USER=postgres" db`

Then using your favorite virtual environment tool (`virtualenv`, `venv`, `conda` etc.) create a new environment and install the `gutensearch` package. The package requires Python 3.7+ For exampe, with `venv`

- `python3 -m venv venv`
- `source venv/bin/activate`
- `python3 -m pip install --upgrade pip`
- `python3 -m pip install --upgrade --no-cache-dir .`

Verify the package has been properly by installed by running

- `gutensearch --help`

you should see the following output

```
usage: gutensearch [-h] {download,load,word,doc} ...

A searchable database for words and documents from Project Gutenberg

positional arguments:
  {download,load,word,doc}
    download            Download documents in a safe and respectful way from
                        Project Gutenberg
    load                Parse and load the word counts from documents into the
                        gutensearch database
    word                Find the documents where the given word occurs most
                        frequently
    doc                 Find the most frequently occuring words in the given
                        document id

optional arguments:
  -h, --help            show this help message and exit
```

If installed properly, you can now load the data into the database in a similar way as shown above (again, assuming the example data provided is one level above your current working directory)

- `gutensearch load --path ../data/ --multiprocessing`

## Usage

You can use the `gutensearch` CLI to easily download documents, parse/load them into the database, and search for words and documents with the following `gutensearch` subprograms available

```
$ gutensearch --help
usage: gutensearch [-h] {download,load,word,doc} ...

A searchable database for words and documents from Project Gutenberg

positional arguments:
  {download,load,word,doc}
    download            Download documents in a safe and respectful way from
                        Project Gutenberg
    load                Parse and load the word counts from documents into the
                        gutensearch database
    word                Find the documents where the given word occurs most
                        frequently
    doc                 Find the most frequently occuring words in the given
                        document id

optional arguments:
  -h, --help            show this help message and exit
```

### `gutensearch download`

To download files from Project Gutenberg, use `gutensearch download`. All downloads make use of the [Aleph Gutenberg Mirror](https://aleph.gutenberg.org/) in order to be respectful to the Project Gutenberg servers, in accordance with their ["robot access" guidelines](https://www.gutenberg.org/policy/robot_access.html). Please see the [complete list of Project Gutenberg Mirrors](https://www.gutenberg.org/MIRRORS.ALL) for more information.

The entire package assumes that document id's are __integers__ and relies on the [Gutenberg Index](https://www.gutenberg.org/dirs/GUTINDEX.ALL) to assign document id's accordingly. Text files downloaded that _may_ have an extension such as `7854-8.txt` or `7854-0.txt` are automatically handled and cleaned during the download process so that the resulting document id is simply `7854` in accordance with the Gutenberg Index.

```
$ gutensearch download --help
usage: gutensearch download [-h] [--path PATH] [--limit LIMIT] [--delay DELAY]
                            [--log-level {notset,debug,info,warning,error,critical}]
                            [--only ONLY | --exclude EXCLUDE | --use-metadata]

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           The path to the directory to store the documents
  --limit LIMIT         Stop the download after a certain number of documents
                        have been downloaded
  --delay DELAY         Number of seconds to delay between requests
  --log-level {notset,debug,info,warning,error,critical}
                        Set the level for the logger
  --only ONLY           Download only the document ids listed in the given
                        file
  --exclude EXCLUDE     Download all document ids except those listed in the
                        given file
  --use-metadata        Use the .meta.json file to determine which documents
                        to download
```

For example, to download the first 1000 documents from Project Gutenberg, run

- `gutensearch download --limit 1000`

This will automatically create a new `data/` directory in the current directory, and begin download documents into `data/`. During the download, metadata is saved every 10 successful downloads and can be inspected in the `.meta.json` file created in `data/.meta.json`.

All documents downloaded are saved as `{id}.txt`. For example, in the `data/` directory

```
$ ls -la | head -15
total 16541544
drwxr-xr-x  21424 k184444  354695482    685568 Oct 27 11:16 .
drwxr-xr-x      3 k184444  354695482        96 Oct 27 10:01 ..
-rw-r--r--      1 k184444  354695482   3868652 Oct 26 10:40 .meta.json
-rw-r--r--      1 k184444  354695482   4462487 Oct 23 12:52 10.txt
-rw-r--r--      1 k184444  354695482    600106 Oct 23 14:09 1000.txt
-rw-r--r--      1 k184444  354695482    101762 Oct 24 22:20 10000.txt
-rw-r--r--      1 k184444  354695482     52510 Oct 24 22:20 10001.txt
-rw-r--r--      1 k184444  354695482    306892 Oct 24 22:20 10002.txt
-rw-r--r--      1 k184444  354695482    380817 Oct 24 22:20 10003.txt
-rw-r--r--      1 k184444  354695482    302750 Oct 24 22:20 10004.txt
-rw-r--r--      1 k184444  354695482    434760 Oct 24 22:20 10005.txt
-rw-r--r--      1 k184444  354695482     95831 Oct 24 22:20 10006.txt
-rw-r--r--      1 k184444  354695482    180139 Oct 24 22:21 10007.txt
-rw-r--r--      1 k184444  354695482    407271 Oct 24 22:21 10008.txt
```

To change where the data is downloaded to (instead of the default `data/` path) use

- `gutensearch download --path files`

where `files/` is the name of the directory where your documents will be saved to. If the directory already exists, it will be used.

If you only want to download a certain subset of documents by their id, create a file containing each integer id on a separate line. For example,

`ids.txt`

```
14130
24088
32918
43440
57076
```

- `gutensearch download --only ids.txt`

this will only download the documents with the id's specified in the file above.

If you want to download __all__ documents _except_ certain ones, you can use the same approach as above except specifying the `--exclude` flag

- `gutensearch download --except ids.txt`

which will download all documents from Project Gutenberg _except_ those specified in the file.

Finally, if a download was interrupted or stopped, you can pick back up to where it left off using the contents of the `.meta.json` file. To do so, run

- `gutensearch download --use-metadata`

which will begin download any files from the Gutenberg Index that are not present in the metadata file.

#### Logging, Error Handling, and Metadata

Unfortunately, some of the document id's in the Gutenberg Index do not have valid url's, or a url that follows the pattern of all the other files. Furthermore, even if the url is valid, there may be no book because the id may be reserved for the future. All of these cases are automatically handled during the download. For example,

```
2020-10-23 15:13:38 [INFO] gutensearch.download.download_gutenberg_documents - [1482/None] Saving document to path: data/1763.txt
2020-10-23 15:13:42 [INFO] gutensearch.download.download_gutenberg_documents - [1483/None] Saving document to path: data/1764.txt
2020-10-23 15:13:46 [ERROR] gutensearch.download.get_site_urls - 404 Client Error: Not Found for url: https://aleph.gutenberg.org/1/7/6/1766/
Traceback (most recent call last):
  File "/Users/k184444/dev/gutensearch/gutensearch/download.py", line 87, in get_site_urls
    response.raise_for_status()
  File "/Users/k184444/Library/Caches/pypoetry/virtualenvs/gutensearch-2L6q6X4M-py3.7/lib/python3.7/site-packages/requests/models.py", line 941, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://aleph.gutenberg.org/1/7/6/1766/
2020-10-23 15:13:46 [INFO] gutensearch.download.download_gutenberg_documents - Skipping document id: 1766
2020-10-23 15:13:49 [ERROR] gutensearch.download.get_site_urls - 404 Client Error: Not Found for url: https://aleph.gutenberg.org/1/7/6/1767/
Traceback (most recent call last):
  File "/Users/k184444/dev/gutensearch/gutensearch/download.py", line 87, in get_site_urls
    response.raise_for_status()
  File "/Users/k184444/Library/Caches/pypoetry/virtualenvs/gutensearch-2L6q6X4M-py3.7/lib/python3.7/site-packages/requests/models.py", line 941, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://aleph.gutenberg.org/1/7/6/1767/
2020-10-23 15:13:49 [INFO] gutensearch.download.download_gutenberg_documents - Skipping document id: 1767
2020-10-23 15:13:54 [INFO] gutensearch.download.download_gutenberg_documents - [1484/None] Saving document to path: data/1770.txt
2020-10-23 15:13:59 [INFO] gutensearch.download.download_gutenberg_documents - [1485/None] Saving document to path: data/1786.txt
```

Progress (including possible errors) are logged by the system and can be saved for further analysis or information if desired. You can change the logging level of the download at runtime by setting the value of `--log-level` to one of `{notset, debug, info, warning, error, critical}`. Logging is handled by the standard builtin Python `logging` library.

For example, to only display warning messages or higher (severity messages), run

- `gutensearch download --log-level warning`

Although logging is helpful for monitoring download progress, the `.meta.json` file is the simplest source of finding information for successfully downloaded files. An example snippet of this file is provided below. Each key represents the id of the document.

`.meta.json`

```json
{
  "5389": {
    "url": "https://aleph.gutenberg.org/5/3/8/5389/",
    "datetime": "2020-10-24 11:54:10",
    "filepath": "/Users/k184444/dev/gutensearch/temp/data/5389.txt"
  },
  "5390": {
    "url": "https://aleph.gutenberg.org/5/3/9/5390/",
    "datetime": "2020-10-24 11:54:15",
    "filepath": "/Users/k184444/dev/gutensearch/temp/data/5390.txt"
  },
  "5391": {
    "url": "https://aleph.gutenberg.org/5/3/9/5391/",
    "datetime": "2020-10-24 11:54:20",
    "filepath": "/Users/k184444/dev/gutensearch/temp/data/5391.txt"
  }
}
```

### `gutensearch load`

Once you have obtained the raw documents (presumably using `gutensearch download`) you'll want to __parse__ and __load__ their contents into the database. The `gutensearch load` command provides an easy interface to perform this task.

> __Warning__ Make sure the Postgres service is available before running this command or else connecting to the database will fail. See the [installation and setup instructions](#installation) above for more information.

```
$ gutensearch load --help
usage: gutensearch load [-h] [--path PATH] [--limit LIMIT] [--multiprocessing]
                        [--log-level {notset,debug,info,warning,error,critical}]

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           The path to the directory containing the documents
  --limit LIMIT         Only parse and load a limited number of documents
  --multiprocessing     Perform the parse/load in parallel using multiple
                        cores
  --log-level {notset,debug,info,warning,error,critical}
                        Set the level for the logger
```

To parse and load documents that are in the `data/` directory, from the current directory run

```
$ gutensearch load
2020-10-27 12:25:05 [INFO] gutensearch.load - Parsing 21421 documents using 1 core
```

which will begin processing every file in the `data/` directory (default `--path`) using a single core.

To specify a different directory name other than `data/` (the default) add the `--path` argument

```
$ gutensearch load --path documents
2020-10-27 12:25:05 [INFO] gutensearch.load - Parsing 21421 documents using 1 core
```

To limit the total number of documents to parse and load, specify a `--limit`

```
$ gutensearch load --limit 50
2020-10-27 12:26:44 [INFO] gutensearch.load - Parsing 50 documents using 1 core
```

Furthermore, for a significant speedup in parsing performance, you can parse multiple documents in parallel by specifying the `--multiprocessing` flag. This is especially useful when parsing a large number of documents at once. Below is an example of the entire parse/load pipeline for 21,400+ documents.

```
$ gutensearch load --path data/ --multiprocessing
2020-10-27 00:31:15 [INFO] gutensearch.load - Parsing 21421 documents using 12 cores
2020-10-27 00:40:42 [INFO] gutensearch.load - Temporarily dropping indexes on table: words
2020-10-27 00:40:42 [INFO] gutensearch.load - Writing results to database
2020-10-27 00:51:18 [INFO] gutensearch.load - Finished writing data to database
2020-10-27 00:51:18 [INFO] gutensearch.load - Truncating table: distinct_words
2020-10-27 00:51:18 [INFO] gutensearch.load - Writing new distinct words to database
2020-10-27 00:53:31 [INFO] gutensearch.load - Finished writing distinct words to database
2020-10-27 00:53:31 [INFO] gutensearch.load - Recreating indexes on table: words
2020-10-27 00:58:22 [INFO] gutensearch.load - Committing changes to database
2020-10-27 00:58:22 [INFO] gutensearch.load - Running vacuum analyze on table: words
2020-10-27 00:58:56 [INFO] gutensearch.load - Committing changes to database
```

In short, the command will identify all `.txt` files available in the specified directory, parse their contents by cleaning/tokenizing each word, and counting unique instances of each token. Then, the data is bulk loaded into Postgres, re-creating indexes and running statistics on the table(s) before exiting. Fore more details on this process, please see the [Discussion and Technical Details](#discussion-and-technical-details) section below.

### `gutensearch word`

With the words and counts of our documents parsed and loaded into the database, we can now perform a variety of interesting searches! The first type of search we can perform is to find the top `n` documents where a given word appears. There are a variety of options and features available.

```
$ gutensearch word --help
usage: gutensearch word [-h] [-l LIMIT] [--fuzzy] [-o {csv,tsv,json}] word

positional arguments:
  word                  The word to search for in the database

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        Limit the total number of results returned
  --fuzzy               Allow search to use fuzzy word matching
  -o {csv,tsv,json}, --output {csv,tsv,json}
                        The output format when printing to stdout
```

For example, to find the 10 documents where the word "fish" shows up most frequently, run

```
$ gutensearch word fish
word    document_id   count
fish	3611	3756
fish	18542	1212
fish	9937	590
fish	8419	545
fish	10136	531
fish	683     405
fish	21008	353
fish	18298	309
fish	4219	309
fish	6745	300
```

By default, the program will limit the results to the top 10 documents found. To change this behavior, set the `--limit` flag to a different option. For example,

```
$ gutensearch word fish --limit 5
word    document_id   count
fish	3611	3756
fish	18542	1212
fish	9937	590
fish	8419	545
fish	10136	531
```

By default, the results will be printed to `stdout` in `tsv` format (tab-separated values). To change this behavior, set the value for the `--output` flag. You can choose from one of three options: `{tsv, csv, json}`, representing tab-separated-values, comma-separated-values, or JSON, respectively. Each are compatible so that you can redirect output directly to a file in a valid output format. For example the same search from above as JSON would be

```
$ gutensearch word fish --output json
[{'count': 3756, 'document_id': 3611, 'word': 'fish'},
 {'count': 1212, 'document_id': 18542, 'word': 'fish'},
 {'count': 590, 'document_id': 9937, 'word': 'fish'},
 {'count': 545, 'document_id': 8419, 'word': 'fish'},
 {'count': 531, 'document_id': 10136, 'word': 'fish'},
 {'count': 405, 'document_id': 683, 'word': 'fish'},
 {'count': 353, 'document_id': 21008, 'word': 'fish'},
 {'count': 309, 'document_id': 18298, 'word': 'fish'},
 {'count': 309, 'document_id': 4219, 'word': 'fish'},
 {'count': 300, 'document_id': 6745, 'word': 'fish'}]
```

or could you save results directly to a CSV file using

```
$ gutensearch word fish --output csv > fish.csv
```

Furthermore, instead of full words you can also provide __word patterns__ such as `fish%` or `doctor_`. Any SQL string pattern is valid and may be used. For example,

```
$ gutensearch word fish% -l 5 -o csv
word,document_id,count
fish,3611,3756
fishing,3611,2036
fishermen,3611,1216
fish,18542,1212
fish,9937,590
```

As we can see, instead of just "fish", the search returned results matching "fish", "fishing", "fisherman" and more.

Finally, you can even execute a search using "fuzzy word matching" for any word that cannot be effectively represented using a word pattern. To enable this behavior, set the `--fuzzy` flag.

```
$ gutensearch word aquaintence -o csv --fuzzy
word,document_id,count
aquaintance,19704,2
aquaintance,3292,1
aquaintance,15772,1
aquaintance,13538,1
aquaintance,3141,1
aquaintance,968,1
aquaintance,947,1
aquaintance,10699,1
aquaintance,16014,1
aquaintance,15864,1
```

As we can see, the search returned results for the "best possible match" for the word "acquaintance", given the provided query had the word misspelled (missing the "c" after "q", and "e" instead of "a"). Fuzzy word matching uses the ["ratio score"](https://docs.python.org/3.9/library/difflib.html#difflib.SequenceMatcher.ratio) algorithm, and picks the word in the available corpus of text in the database with the highest ratio to the provided word. For more details, please see the [Discussion and Technical Details](#discussion-and-technical-details) section below.

### `gutensearch doc`

We've seen how to search for all documents for a specific word, but what if we want to do the opposite? To perform a search for the top `n` most frequently used words in a given document (id) we can use `gutensearch doc`.

```
$ gutensearch doc --help
usage: gutensearch doc [-h] [-l LIMIT] [-m MIN_LENGTH] [-o {json,csv,tsv}] id

positional arguments:
  id                    The document id to search for

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        Limit the total number of results returned
  -m MIN_LENGTH, --min-length MIN_LENGTH
                        Exclude any words in the search less than a minimum
                        character length
  -o {json,csv,tsv}, --output {json,csv,tsv}
                        The output format when printing to stdout
```

For example, to the find the top 10 most frequent words in the document with id `8419`,

```
$ gutensearch doc 8419
word	document_id	count
which	8419	7601
this	8419	7189
with	8419	6922
they	8419	5003
that	8419	4714
river	8419	4495
from	8419	4272
their	8419	3244
them	8419	3150
about	8419	2860
```

Similar to before, by default, the program will limit the results to the top 10 documents found. To change this behavior, set the --limit flag to a different option. For example,

```
$ gutensearch doc 8419 --limit 5
word	document_id	count
which	8419	7601
this	8419	7189
with	8419	6922
they	8419	5003
that	8419	4714
```

Once again, the results printed to `stdout` are in `tsv` format by default. To change this behavior, use the `--output` flag, choosing from one of the three options: `{tsv, csv, json}`

```
gutensearch doc 8419 --output json
[{'count': 7601, 'document_id': 8419, 'word': 'which'},
 {'count': 7189, 'document_id': 8419, 'word': 'this'},
 {'count': 6922, 'document_id': 8419, 'word': 'with'},
 {'count': 5003, 'document_id': 8419, 'word': 'they'},
 {'count': 4714, 'document_id': 8419, 'word': 'that'},
 {'count': 4495, 'document_id': 8419, 'word': 'river'},
 {'count': 4272, 'document_id': 8419, 'word': 'from'},
 {'count': 3244, 'document_id': 8419, 'word': 'their'},
 {'count': 3150, 'document_id': 8419, 'word': 'them'},
 {'count': 2860, 'document_id': 8419, 'word': 'about'}]
```

By default, the optional `--min-length` flag is set to 4 characters. This behavior excludes any words from the search that are less than a minimum character length. The default is set to 4 to avoid commonly encountered words such as "a" or "the". To increase the minimum character length, simply provide a different (integer) value to `--min-length` as shown in the example below

```
$ gutensearch doc 8419 --min-length 12
word	document_id	count
considerable	8419	274
neighbourhood	8419	229
particularly	8419	136
sufficiently	8419	106
observations	8419	88
disagreeable	8419	84
notwithstanding	8419	53
considerably	8419	49
perpendicular	8419	48
circumstance	8419	46
```

## Troubleshooting

The following section outlines a few problems you may (but hopefully don't) encounter when installing, setting-up, and running the project.

__A directory that has been mounted to a container appears empty__

Make sure that the data directory you are attempting to mount __is not__ in the same directory as the `.dockerignore` file. In specific, the `.dockerignore` file ignores anything under `/data/` to avoid unnecessarily sending large amounts of data to the Docker daemon when building containers.

__Docker kills a task/process when loading data into the database__

If you are attempting to parse/load a large number of documents at once, you may run into memory issues with Docker. The default setting in the `cli` service in `docker-compose.yml` is set to 1 gigabyte. However, if you're only building and running the cli image independently, you may need to include a `--memory` flag during `docker run`. See the [Docker resource constraints documentation](https://docs.docker.com/config/containers/resource_constraints/#memory) for more information.

## Discussion and Technical Details

The project is essentially divided into four different pieces, each responsible for different tasks in the entire workflow.

- `cli.py`: Contains the code for the command-line-interface implementation and provides the `main()` function as the entrypoint for the entire interface
- `database.py`: This module contains any database-related code and functions. Most of these are utilities for connecting to and querying the database. Furthermore, this module includes two functions for searching for words or documents from the database.
- `download.py`: This module provides the implementations for downloading and saving data from Project Gutenberg, including building up the appropriate URL patterns, downloading a document, and saving documents.
- `parse.py`: This module contains any parsing related functions, mostly related to parsing the contents of a document, cleaning it, "tokenization", and counting unique instance of words.

### Design

The project and code is designed in such a way that a "client" can choose to download all or some of the files (by their unique document id) locally, then parse and load them into the database. The database chosen was Postgres because it is what I'm most familiar with, and with a few simple indexing strategies provides excellent performance for the search requirements provided. Because Postgres supports concurrent reads/writes from multiple clients, it's a suitable choice for the database if this program was being executed on multiple machines at once. Although there is no mechanism in the current implementation for synchronization of files downloaded between multiple machines, this could be added by the use of a distributed task queue such as Celery. Aside from that, the current implementation is suitable for downloading and parsing documents from Project Gutenberg, and loading the tokenized word counts into a single database.

### Document ID

One aspect of the design that needed to be considered would be how documents would be identified. Luckily, it turns out that Project Gutenberg provides their own [Gutenberg Index](https://www.gutenberg.org/dirs/GUTINDEX.ALL). Unfortunately, I could not find a "machine-readbale" format (despite a lot of digging around) so this needed to be parsed. However, this was not a big problem as it could be parsed once (only takes a few seconds) and then saved locally for any future use. The `gutenberg-index.txt` file in the source code provides a list of every document id listed on Project Gutenberg. This was the key to making the download implementations simple and straightforward.

It turns out that documents saved on Project Gutenberg (the `aleph.gutenberg.org` mirror in specific) follow a very specific url pattern. Once I realized that this pattern existed, it made constructing url's for a given document id very simple. For example, for document with id `6131` has the following url pattern: `https://aleph.gutenberg.org/6/1/3/6131/`. If you follow the link, you'll see that this is a directory of several files, including both text and zip files. At this point, I realized a small possible issue that required I add a little bit of complexity to my design. In this particular example, you'll notice there are more than one text file, `6131-0.txt` and `6131.txt`. As far as I could tell, the contents of these two files were identical (I checked around 10 or so random documents and this proved to be the case for all of them, but I could have missed something, and this may not be the case for _all_ documents). Furthermore, some documents only have a single text file (some with the trailing -0 and others without) while other documents had a trailing -8 in their name. For this reason, I decided that my download pattern for a given document id would be as follows:

1. Construct url for a given document id. Ex: given id `6131` return `https://aleph.gutenberg.org/6/1/3/6131/`
2. Make a request to this url, and check that it's valid, no 404's are thrown etc.
3. If valid, find all links on the site (`<a>` tags) ending with `.txt` and store them
4. If more than one `.txt` file was found, keep the first one found in this order of precedence: `{id}.txt`, `{id}-0.txt`, `{id}-8.txt`

Once a document was successfully downloaded, it was saved to the target directory with the name `{id}.txt`, regardless of the name used when being downloaded.

### Parsing Strategy

Once one or more documents are available locally (in whatever directory name the user wants, `data/` by default) the user can load them into the database. But, before this is done each document needs to be parsed, tokenized, and unique word instances must be counted. For this step, I tried to take the simplest approach possible in order to keep the code readable and as performant as possible.

The entire parsing pipeline only requires a single pass over the document text to be cleaned and tokenized, and then one more pass to count unique words. If you inspect the implementatin of `gutensearch.parse.lazytokenize` you'll see that this function returns a generator. This generator will iterate through each character in the given body of text. Each character encountered is added to a `word` "buffer", then `yield`ed to the user , and the `word` buffer flushed when an "invalid" character was encountered. Only upper or lower case letter characters were considered valid (ASCII decimal values between 65 and 90, and 97 and 122). Whenever a valid character was stored in the `word` buffer, it was saved as lower case. A "lazy" strategy was chosen so that theoretically, a document that could not fit in memory all at once could still be efficiently parsed. Furthermore, this function is pure and produces no side-effects which makes it ideal to be used in a parallelized setting.

Once a document was parsed and cleaned, I made use of the built-in Python [`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter) class from the `collections` module to count unique instances of each word. In conjunction with the lazy tokenizer described above, I implemented the `gutensearch.parser.parse_document` function to parse, tokenize, and count word instances for a given document. This function can optionally be used with `multiprocessing` which is an option provided to the user as part of the `gutensearch load` command.

### Database Design

As briefly discussed above, Postgres was chosen for this project because I am familiar with it, it is high performance, and full-featured. The database only contains two tables, `words` and `distinct_words`. The schema for this database can be found in `schema.sql` in this directory. We'll focus on `words` first.

The `words` table consists of three columns, `word`, `document_id`, and `count`. It contains all of the records parsed from the sections described above. Each record contains a single word, the document id that it was found in, and the frequency (count) that it occurred. The key to making searches fast and effective over this table was to creating two indexes over this table. The first is an index on `words` over the column `word`. This allows for fast, indexed look-up of a specific word. Furthermore, the second index is an index on `words` over the column `document_id` which similarly provides fast, indexed look-up of a specific document in the table. Both of these indexes are effective because the cardinality of the columns are _relatively_ small compared to the total number of records in the entire table. For the case analyzed with 21,421 unique documents containing over 134 million rows there were roughly 3.4 million unique words. Therefore, we'd expect that on average, searches for unique documents is faster than for unique words. Please see the [benchmarks](#benchmarks) section for more information.

The second table, `distinct_words` is a table with a single column `word` and contains every unique (distinct) instance of a word in the `words` table. The idea behind this table was to provide a pre-computed set that could be used as a corpus for performing fuzzy word matching. It turned out in practice that this was an ineffective approach for performing fuzzy word matching as querying the `distinct_words` table whenever a fuzzy word match was requested (in addition to finding the closest match) was still relatively slow. Although __word pattern__ matching using SQL string patterns still proved to be effective, if true fuzzy word matching was a hard requirement for this project, more work would need to be done to improve this aspect of the performance.

### Database Loading Strategy

It can be tricky to efficiently load a large number of records into a table at once, especially in a relational database. However, Postgres provides a few [helpful tips](https://www.postgresql.org/docs/current/populate.html) for performing "bulk loads" efficiently. I have made use of a few of these suggestions in my loading implementation. In short, after all documents have been parsed into words and counts, they are still in memory. In order to effectively write all of the data to the the `words` table described above, I make use of the `COPY FROM` command which allows for loading all of the rows in a single command instead of a series of `INSERT` commands. In order to do this, [`psycopg2.cursor.copy_from`](https://www.psycopg.org/docs/cursor.html#cursor.copy_from) expects an instance of of an `IO` object. Writing all of the data as a single text file to disk, then reading it back in to memory would have been slow and ineffective. Instead, I made use of the [`io.StringIO`](https://docs.python.org/3/library/io.html#io.StringIO) class to incrementally build up a in-memory text buffer. Each record was written as tab-delimited values to the text buffer (as expected by Postgres) then efficiently written into the `words` database. Prior to performing this operation, any indexes on `words` were dropped, then later re-created after writing the data. Furthermore, after all of the data had been written, a `VACUUM ANALYZE` command was also dispatched to provide further optimizations and up-to-date statistics that are used to improve the performance of the query planner. This strategy was used to effectively store over 134+ million records in around 8.5 minutes, after parsing 21,000+ documents. Please see the [benchmarks](#benchmarks) section below for more information.

### Fuzzy Word Matching

As mentioned in the [database design](#database-design) section above, this project provides a fuzzy word matching feature that can be used when searching for words in the database. I took a simple approach inspired by the following [blog post from SeatGeek](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/) when announcing the open-sourcing of their [`fuzzywuzzy`](https://github.com/seatgeek/fuzzywuzzy) package. I opted not to include `fuzzywuzzy` as part of my project in order to keep the dependencies as minimal as possible. Instead, I created a custom function (found under `gutensearch.parse.closest_match`) that makes use of the Python built-in [`SequenceMatcher`](https://docs.python.org/3.9/library/difflib.html#difflib.SequenceMatcher) object. Given a word and a corpus of words, the function will return a word from the corpus that most closely matches the given word by choosing the word with the highest "ratio". If there are any ties, they are resolved by selecting the first instance of the highest ratio found in the corpus. More information on the performance of this implementation in practice, please see the [benchmarks](#benchmarks) below.

## Benchmarks

This section is mainly focused on the performance of the parsing, loading, and searching components of this project. All figures and benchmarks performed are only meant to be loosely interpreted for instructional use and context. They have been performed on a Macbook Pro (16 inch, 2019) with 2.6 GHz 6-Core Intel Core i7 processors, and 16 GB 2667 MHz DDR4 of RAM.

### Parsing

The first part of `gutensearch load` includes parsing the contents of every document in the provided directory. From the logs of running `gutensearch load --path data/ --multiprocessing` on a directory with 21,421 documents (of varying size and length) using all 6 cores (12 threads), the program __parsed__ 134,855,452 records in __567 seconds__.

```
2020-10-27 00:31:15 [INFO] gutensearch.load - Parsing 21421 documents using 12 cores
2020-10-27 00:40:42 [INFO] gutensearch.load - Temporarily dropping indexes on table: words
```

```python
from gutensearch.database import query

records = query('SELECT COUNT(*) AS count FROM words')
count = records[0].count
print(count)
```

```
134855452
```

This equates to roughly __37.8 documents parsed per second__, or __237,840 records parsed per second__, on average.

### Loading

After documents have been parsed in memory, they need to be efficiently bulk-loaded into the database. Once again, from the logs of running `gutensearch load --path data/ --multiprocessing` on a directory with 21,421 documents (of varying size and length) using all 6 cores (12 threads), the program __loaded__ 134,855,452 records in __504 seconds__.

```
2020-10-27 00:40:42 [INFO] gutensearch.load - Writing results to database
2020-10-27 00:51:18 [INFO] gutensearch.load - Finished writing data to database
```

This equates to roughly __267,570 records loaded into the table per second__, on average.

### Word Search

For a database with over 134+ million records, we have the following benchmarks. These were timed using the following setup in an `ipython` terminal using the `%timeit` cell magic. These are likely _optimistic_ estimates since the same word/pattern is repeatedly being searched for in a single `%timeit` block of loops.

```python
>>> from gutensearch.database import search_word
>>> %timeit search_word(...)
```

| Word | Fuzzy | Limit | Result |
|:-:|:-:|:-:|-|
| fish | FALSE | 10 | 38.9 ms ± 690 µs per loop (mean ± std. dev. of 7 runs, 10 loops each) |
| acceptance | FALSE | 10 | 31.6 ms ± 12.9 ms per loop (mean ± std. dev. of 7 runs, 1 loop each) |
| consumable | FALSE | 10 | 9.43 ms ± 656 µs per loop (mean ± std. dev. of 7 runs, 100 loops each) |
| fish% | FALSE | 10 | 19.6 s ± 964 ms per loop (mean ± std. dev. of 7 runs, 1 loop each) |
| doctor_ | FALSE | 10 | 18.4 s ± 533 ms per loop (mean ± std. dev. of 7 runs, 1 loop each) |
| %ing | FALSE | 10 | 31.7 s ± 930 ms per loop (mean ± std. dev. of 7 runs, 1 loop each) |
| aquaintence | TRUE | 10 | 1min 24s ± 1.98 s per loop (mean ± std. dev. of 7 runs, 1 loop each) |

#### Fuzzy Word Matching

For a database with over 3.4+ million unique words, we have the following benchmarks. The first is the typical time taken to query the entire "corpus" of distinct words from the database, and the second benchmarks the performance of performing a fuzzy word match against the corpus of text.

```python
>>> from gutensearch.database import query_distinct_words
>>> %timeit query_distinct_words()
```

```
3.8 s ± 254 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

```python
>>> from gutensearch.parse import closest_match
>>> from gutensearch.database import query_distinct_words
>>>
>>> corpus = query_distinct_words()
>>> %timeit closest_match('aquaintence', corpus)
```

```
1min 25s ± 1.27 s per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

### Document Search

For a database with over 134+ million records, we have the following benchmarks. These were timed using the following setup in an `ipython` terminal using the `%timeit` cell magic. These are likely _optimistic_ estimates since the same document is repeatedly being searched for in a single `%timeit` block of loops.

```python
>>> from gutensearch.database import search_document
>>> %timeit search_document(...)
```

| Document ID | Min Length | Limit | Result |
|:-:|:-:|:-:|-|
| 8419 | 4 | 10 | 31.4 ms ± 786 µs per loop (mean ± std. dev. of 7 runs, 10 loops each) |
| 8419 | 8 | 10 | 22 ms ± 1.25 ms per loop (mean ± std. dev. of 7 runs, 10 loops each) |
| 8419 | 12 | 10 | 13.4 ms ± 565 µs per loop (mean ± std. dev. of 7 runs, 100 loops each) |
| 8419 | 16 | 10 | 11.8 ms ± 107 µs per loop (mean ± std. dev. of 7 runs, 100 loops each) |
| 8419 | 20 | 10 | 12.2 ms ± 356 µs per loop (mean ± std. dev. of 7 runs, 100 loops each) |

## Future Work

In summary, the core requirements of this project have been met and provide satisfactory performance (between 8-40 ms on average for an exact word match, and 8-30 ms on average for a document id search). Furthermore, the command-line-interface provides a variety of features for downloading, parsing, loading, and performing various kinds of searches over the data. However, there is always room for improvement. Depending on the needs of the project, the following are a few possible enhancements and improvements that can be made to this project:

- Improve performance of fuzzy word matching. This would require some research and learning on my end, as I don't have much experience working with large amounts of text data.
- Possibility to directly parse and load a document into the database directly after download without saving to disk. This could help improve performance, and simplify the overall data acquisition and ETL process.
- Possibility for an "online" system that is constantly getting a list of document id's to download, parsing them, and loading them into the database. This could potentially be done using a distributed task queue that provides a queue of documents that need to be processed.