import json
import os
import signal
from multiprocessing import Pool

import dotenv
from web3 import Web3, HTTPProvider

from src.utils.contract_wrapper import ContractWrapper
from utils.tools import to_address, get_ABI

dotenv.load_dotenv(verbose=True, override=True)

# load and store database
nonces = {}
mount_point = os.getenv("ORACLE_DATA")
try:
    with open(f"{mount_point}/db.json", "r") as f:
        nonces = json.load(f)
except:
    pass


def exit_gracefully(*args):
    with open(f"{mount_point}/db.json", "w") as f:
        json.dump(nonces, f)


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

# Config
priv_key = os.getenv("PRIVKEY")
acc = to_address(priv_key)

contract_addr = os.getenv("LEFT_ADDRESS"), os.getenv("RIGHT_ADDRESS")
gas = int(os.getenv("LEFT_GASPRICE")), int(os.getenv("RIGHT_GASPRICE"))
sb = int(os.getenv("LEFT_START_BLOCK")), int(os.getenv("RIGHT_START_BLOCK"))

web3 = Web3(HTTPProvider(os.getenv("LEFT_RPCURL"))), Web3(HTTPProvider(os.getenv("RIGHT_RPCURL")))

# Contracts
abi = get_ABI("contracts/", "Bridge")

contract = [
    ContractWrapper(w3=web3[i], gas=gas[i], user_pk=priv_key, abi=abi, address=contract_addr[i])
    for i in range(len(contract_addr))
]


def parse(event):
    raw_data = event['data'][2:]
    print(raw_data)
    return Web3.toChecksumAddress(raw_data[24:64]), int(raw_data[-64:], base=16)


def process(addr, amount):
    pass


flt = [contract[i].events.bridgeActionInitiated(fromBlock=sb[i]) for i in range(2)]


def update(i):
    for event in web3[i].eth.getFilterChanges(flt[i].filter_id):
        process(*parse(event))


def main():
    with Pool(2) as p:
        p.map(update, range(1))


if __name__ == '__main__':
    main()
