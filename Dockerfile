FROM python:3.9-slim

WORKDIR /deployment

RUN apt update
RUN apt install -y gcc musl-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /deployment/run.sh
