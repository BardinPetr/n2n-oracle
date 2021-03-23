FROM python:3.9-slim

WORKDIR /deployment

RUN apt update
RUN apt install -y gcc musl-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt install -y wget
RUN wget -O /usr/bin/solc-v0.7.6 https://solc-bin.ethereum.org/linux-amd64/solc-linux-amd64-v0.7.6+commit.7338295f
RUN chmod +x /usr/bin/solc-v0.7.6

COPY . .

RUN chmod +x /deployment/run*
