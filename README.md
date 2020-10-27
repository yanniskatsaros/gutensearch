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
- [Benchmarks](#benchmarks)
- [Future Work](#future-work)

## Installation

The simplest way to install and run the project is using `docker` and `docker-compose`. To get started, in this directory (containing the `docker-compose.yml` file) run (or `docker-compose up --build -d` to run in detached mode)

- `docker-compose up --build`

This will build and start three services. The first is an empty Postgres database that has been initialized with the correct schema, and the second is the project documentation. Head over to `localhost:8000` on your browser to check them out! The third build is the project command-line-interface. 

Once Docker compose has finished setting up, you can run the container with the command-line-interface installed using

- `docker-compose run cli`

Depending on how many documents you are working with, you _may or may not_ need to tune the memory limits in the `docker-compose.yml` file prior to bringing the services up. See the [troubleshooting](#troubleshooting) section below for more details if necessary.

If you have already downloaded data locally using `gutensearch download` (see the [usage](#download) section below), you can mount the volume to the container at runtime. For example, if the `data/` directory is on your desktop,

- `docker-compose run -v "/Users/username/Desktop/data/:/data" cli`

If you run into any issues, please see the [troubleshooting](#troubleshooting) section below.

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

...

## Benchmarks

...

## Future Work

...
