# syntax=docker/dockerfile:1
FROM mysql
ENV MYSQL_DATABASE=atm
ENV MYSQL_ROOT_PASSWORD=password
COPY schema.sql /docker-entrypoint-initdb.d/