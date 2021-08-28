# syntax=docker/dockerfile:1
FROM python:3.9.6
WORKDIR /server
CMD apt install libmariadb3 libmariadb-dev
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 56789
COPY ./src/* .
ENV MYSQL_HOST=mariadb
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=password
ENV MYSQL_DB=atm
CMD ["python", "-u", "Main.py"]