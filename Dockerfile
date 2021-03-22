FROM python:3.9-alpine

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN pip install web3

COPY . .