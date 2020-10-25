FROM python:3.9-slim-buster
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN python -m pip install .
ENTRYPOINT [ "/bin/bash" ]