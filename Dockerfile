FROM python:3.10.5-alpine3.16
WORKDIR /usr/src/bot
RUN apk update && \
    apk add --no-cache mariadb-dev gcc libc-dev libffi-dev g++
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt