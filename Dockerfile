FROM python:3.9-alpine

WORKDIR /deployment

RUN apk add --no-cache --virtual .build-deps gcc musl-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

#RUN mkdir solcx
#RUN wget -O /deployment/solcx/solc-v0.7.6 https://solc-bin.ethereum.org/linux-amd64/solc-linux-amd64-v0.7.6+commit.7338295f
#RUN chmod +x /deployment/solcx/solc-v0.7.6

COPY . .

RUN chmod +x /deployment/run.sh
