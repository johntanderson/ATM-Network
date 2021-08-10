# syntax=docker/dockerfile:1
FROM python:3.9.6-alpine
WORKDIR /server
RUN apk add --no-cache gcc musl-dev linux-headers
COPY ../requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 56789
COPY ./src/* .
ENV MYSQL_HOST=mysql
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=password
ENV MYSQL_DB=atm
CMD ["python", "-u", "Main.py"]