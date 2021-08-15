# syntax=docker/dockerfile:1
FROM mariadb
ENV MARIADB_DATABASE=atm
ENV MARIADB_ROOT_PASSWORD=password
COPY schema.sql /docker-entrypoint-initdb.d/