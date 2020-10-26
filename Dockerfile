FROM python:3.9-slim-buster
RUN mkdir /code
WORKDIR /code

COPY pyproject.toml /code/
COPY gutensearch /code/gutensearch

RUN python -m pip install .

ENTRYPOINT [ "/bin/bash" ]