import json
import os
import signal

import dotenv
from web3 import Web3, HTTPProvider

from src.utils.contract_wrapper import ContractWrapper
from utils.tools import to_address, get_ABI

dotenv.load_dotenv(verbose=True, override=True)

# load and store database
#nonces = {}
mount_point = os.getenv("ORACLE_DATA")
try:
    with open(f"{mount_point}/db.json", "r") as f:
        #nonces = json.load(f)
        pass
except:
    pass


def exit_gracefully(*args):
    with open(f"{mount_point}/db.json", "w") as f:
        #json.dump(nonces, f)
        pass


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

# Config
priv_key = os.getenv("PRIVKEY")
acc = to_address(priv_key)

contract_addr = (os.getenv("LEFT_ADDRESS"), os.getenv("RIGHT_ADDRESS"))
gas = (int(os.getenv("LEFT_GASPRICE")), int(os.getenv("RIGHT_GASPRICE")))
sb = (int(os.getenv("LEFT_START_BLOCK")), int(os.getenv("RIGHT_START_BLOCK")))

web3 = (Web3(HTTPProvider(os.getenv("LEFT_RPCURL"))), Web3(HTTPProvider(os.getenv("RIGHT_RPCURL"))))

# Contracts
abi = get_ABI("contracts/", "BridgeSide")

contract = [
    ContractWrapper(w3=web3[i], gas=gas[i], user_pk=priv_key, abi=abi, address=contract_addr[i])
    for i in range(len(contract_addr))
]

def main():
    # transfer initial balances
    traced_balance = [web3[i].eth.getBalance(contract_addr[i]) for i in range(2)]

    for i in range(2):
        j = (i + 1) % 2
        if traced_balance[i] != contract[j].getLiquidityLimit():
            contract[j].updateLiquidityLimit(traced_balance[i])
    
    # main loop
    while True:
        for i in range(2):
            balance = web3[i].eth.getBalance(contract_addr[i])
            if balance != traced_balance[i]:
                traced_balance[i] = balance

                j = (i + 1) % 2
                traced_balance[j].updateLiquidityLimit(balance)



if __name__ == '__main__':
    main()
