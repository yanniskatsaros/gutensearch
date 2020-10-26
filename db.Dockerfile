# see: https://stackoverflow.com/a/34753186
FROM postgres:13-alpine
COPY schema.sql /docker-entrypoint-initdb.d/