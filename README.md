# `gutensearch` :mag: :books:
A searchable database and command-line-interface for words and documents from Project Gutenberg

## Installation

The simplest way to install and run the project is using `docker` and `docker-compose`. To get started, in this directory (containing the `docker-compose.yml` file) run

`docker-compose up --build` (or `docker-compose up --build -d` to run in detached mode)

This will build and start three services. The first is an empty Postgres database that has been initialized with the correct schema, and the second is the project documentation. Head over to `localhost:8000` on your browser to check them out! The third build is the project command-line-interface. 

Once Docker compose has finished setting up, you can run the container with the command-line-interface installed using

`docker-compose run cli`

If you have already downloaded data locally using `gutensearch download` (see the [usage](#usage) section below), you can mount the volume to the container at runtime using

`docker-compose run -v "/Users/k184444/Desktop/data/:/data" cli`

### Lightweight Installation

Alternatively, for a more "lightweight" installation where only the Postgres database is containerized, run

`docker build -t db -f db.Dockerfile .`

to build and tag the Postgres image. To start the database, run

`docker run -d --rm --name db -p 5432:5432 --shm-size=1g -e "POSTGRES_DB=postgres" -e "POSTGRES_PASSWORD=postgres" -e "POSTGRES_USER=postgres" db`

Then using your favorite virtual environment tool (`virtualenv`, `venv`, `conda` etc.) create a new environment and install the `gutensearch` package. The package requires Python 3.7+ For exampe, with `venv`

- `python3 -m venv venv`
- `source venv/bin/activate`
- `python3 -m pip install --upgrade pip`
- `python3 -m pip install --upgrade --no-cache-dir .`

Verify the package has been properly by installed by running

`gutensearch --help`

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

## Setup

...