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

...

### `gutensearch word`

...

### `gutensearch doc`

...

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
