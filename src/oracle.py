import json
import logging
import os
import signal
import sys
import time

import dotenv
from web3 import Web3, HTTPProvider, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy, construct_time_based_gas_price_strategy

from utils.contract_wrapper import ContractWrapper
from utils.tools import install_solc, to_address, get_ABI

dotenv.load_dotenv(verbose=True, override=True)
logging.basicConfig(level=logging.INFO)

in_docker = "/deployment" in os.getcwd()
mount_point = ("/data" if in_docker else os.getenv("ORACLE_DATA")).removesuffix("/")
logfile = f"{mount_point}/{int(time.time())}.log"


def log(*args, console=True):
    if console:
        logging.info(*args)
    try:
        with open(logfile, "a") as f:
            print(f"[{time.ctime()}]", *args, file=f)
    except FileNotFoundError:
        pass


log("\n\n" + "#" * 15 + "\n\n")
log("Started")
if in_docker:
    install_solc()
log("Solc prepared")

# Config
priv_key = os.getenv("PRIVKEY")
acc = to_address(priv_key)

contract_addr = (os.getenv("LEFT_ADDRESS"), os.getenv("RIGHT_ADDRESS"))
gas = (int(os.getenv("LEFT_GASPRICE")), int(os.getenv("RIGHT_GASPRICE")))
sb = (int(os.getenv("LEFT_START_BLOCK")), int(os.getenv("RIGHT_START_BLOCK")))

# load and store database
processed = {
    0: sb[0],
    1: sb[1]
}
try:
    with open(f"{mount_point}/db.json", "r") as f:
        processed = json.load(f)
except:
    pass


def exit_gracefully(*args):
    global processed
    log(f"Saving {len(processed.keys())} items")
    try:
        processed = {i: web3[i].eth.get_block('latest').number for i in range(2)}
        with open(f"{mount_point}/db.json", "w") as f:
            json.dump(processed, f)
    finally:
        sys.exit(0)


for i in [signal.SIGINT, signal.SIGTERM]:
    signal.signal(i, exit_gracefully)


def create(x):
    w = Web3(HTTPProvider(os.getenv(x + "_RPCURL")))
    w.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w


web3 = [create(i) for i in ["LEFT", "RIGHT"]]

# Contracts
abi_path = "src/contracts/abi.json"
abi = None
try:
    with open(abi_path, "r") as f:
        abi = json.load(f)
except:
    abi = get_ABI("src/contracts/", "BridgeSide")
    json.dump(abi, open(abi_path, "w"))

contract = [
    ContractWrapper(w3=web3[i], gas_price=gas[i], user_pk=priv_key, abi=abi, address=contract_addr[i])
    for i in range(len(contract_addr))
]

latest_event_where_im_not_a_validator = [None, None]


def update(flt, startup=False):
    found_any = [False, False]
    for i in range(2):
        j = (i + 1) % 2

        if latest_event_where_im_not_a_validator[i] is not None:
            try:
                contract[j].commit(*latest_event_where_im_not_a_validator[i])
                latest_event_where_im_not_a_validator[i] = None
            except ContractLogicError as e:
                if str(e).find("!validator") == -1:
                    latest_event_where_im_not_a_validator[i] = None
                    found_any[i] = True
        else:
            logs = flt[i].get_all_entries()  # if startup else flt[i].get_new_entries()

            for e in logs:
                data = (e['args']['recipient'], e['args']['amount'], e['transactionHash'].hex())
                found_any[i] = True

                # log(f"NEW event on NET{i} from {data[0]} with amount {data[1]} with ID{xid}")
                try:
                    contract[j].commit(*data)
                except ContractLogicError as e:
                    if str(e).find("!validator") != -1:
                        latest_event_where_im_not_a_validator[i] = data
                except Exception as ex:
                    log(str(ex))

        if found_any[i]:
            processed[i] = web3[i].eth.get_block('latest').number

    return found_any[0] or found_any[1]


def main():
    try:
        log(f"Working from {acc}")

        flt = [contract[i].events.bridgeActionInitiated.createFilter(fromBlock=processed[i]) for i in range(2)]

        log("Running first update")
        update(flt, startup=True)

        log("Updating old events completed. Running continuously")
        try:
            while True:
                update(flt)
        except KeyboardInterrupt:
            exit_gracefully()
    except Exception as e:
        log(str(e))


if __name__ == "__main__":
    main()
