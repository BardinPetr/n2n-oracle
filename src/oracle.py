import json
import logging
import os
import signal
import sys
import time

import dotenv
from web3 import Web3, HTTPProvider
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware

from utils.contract_wrapper import ContractWrapper
from utils.tools import install_solc, to_address, get_ABI

dotenv.load_dotenv(verbose=True, override=True)
logging.basicConfig(level=logging.INFO)

mount_point = ("/data" if "deployment" in os.getcwd() else os.getenv("ORACLE_DATA")).removesuffix("/")
logfile = f"{mount_point}/{int(time.time())}.log"


def log(*args, console=True):
    if console:
        logging.info(*args)
    with open(logfile, "a") as f:
        print(f"[{time.ctime()}]", *args, file=f)


log("Started")
install_solc()
log("Solc prepared")

# # load and store database
processed = {}
try:
    with open(f"{mount_point}/db.json", "r") as f:
        processed = json.load(f)
except:
    pass


def exit_gracefully(*args):
    log(f"Saving {len(processed.keys())} items")
    with open(f"{mount_point}/db.json", "w") as f:
        json.dump(processed, f)
    sys.exit(0)


for i in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(i, exit_gracefully)

# Config
priv_key = os.getenv("PRIVKEY")
acc = to_address(priv_key)

contract_addr = (os.getenv("LEFT_ADDRESS"), os.getenv("RIGHT_ADDRESS"))
gas = (int(os.getenv("LEFT_GASPRICE")), int(os.getenv("RIGHT_GASPRICE")))
sb = (int(os.getenv("LEFT_START_BLOCK")), int(os.getenv("RIGHT_START_BLOCK")))


def create(x):
    w = Web3(HTTPProvider(os.getenv(x + "_RPCURL")))
    w.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w


web3 = [create(i) for i in ["LEFT", "RIGHT"]]
# web3 = (Web3(HTTPProvider(os.getenv("LEFT_RPCURL"))), Web3(HTTPProvider(os.getenv("RIGHT_RPCURL"))))

# Contracts
abi = get_ABI("src/contracts/", "BridgeSide")

contract = [
    ContractWrapper(w3=web3[i], gas=gas[i], user_pk=priv_key, abi=abi, address=contract_addr[i])
    for i in range(len(contract_addr))
]

latest_event_where_im_not_a_validator = (None, None)


def update(flt, startup=False):
    found_any = False
    for i in range(2):
        j = (i + 1) % 2

        if latest_event_where_im_not_a_validator[i] is not None:
            xid = latest_event_where_im_not_a_validator[i][2]
            try:
                contract[j].commit(*latest_event_where_im_not_a_validator[i])
                processed[xid] = int(time.time())
                latest_event_where_im_not_a_validator[i] = None
            except ContractLogicError as e:
                if str(e).find("!validator") == -1:
                    latest_event_where_im_not_a_validator[i] = None
            return False

        logs = flt[i].get_all_entries() if startup else flt[i].get_new_entries()
        for e in logs:
            data = (e['args']['recipient'], e['args']['amount'], int.from_bytes(e['transactionHash'], 'big'))
            tid = Web3.solidityKeccak(['address', 'uint256', 'uint32'], data)
            xid = tid.hex()
            found_any = True
            if xid not in processed:
                log(f"NEW event on NET{i} from {data[0]} with amount {data[1]} with ID{xid}")
                try:
                    contract[j].commit(*data[:-1], xid)
                    log(f"Confirmed ID{xid}")
                    processed[xid] = int(time.time())
                except ContractLogicError as e:
                    if str(e).find("!validator") != -1:
                        latest_event_where_im_not_a_validator[i] = (*data[:-1], xid)
                    log(f"Failed for {xid}")
                except Exception as ex:
                    log(f"Failed for {xid}", ex)
                    # TODO: maybe save failed commit
            else:
                log(f"OLD event on NET{i} from {data[0]} with amount {data[1]} with ID{xid}")
    return found_any


def main():
    log(f"Working from {acc}")

    flt = [contract[i].events.bridgeActionInitiated.createFilter(fromBlock=sb[i]) for i in range(2)]

    log("Running first update")
    if not update(flt, startup=True):
        pass  # TODO: Add initialization of contracts

    log("Updating old events completed. Running continuously")
    try:
        while True:
            update(flt)
    except KeyboardInterrupt:
        exit_gracefully()


if __name__ == "__main__":
    main()
