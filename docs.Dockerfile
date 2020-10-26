FROM python:3.9-slim-buster

RUN mkdir /code
WORKDIR /code

COPY pyproject.toml mkdocs.yml docs-requirements.txt /code/
COPY gutensearch /code/gutensearch
COPY docs /code/docs

RUN python -m pip install -r docs-requirements.txt
RUN python -m pip install .

EXPOSE 8000

CMD [ "mkdocs", "serve"]