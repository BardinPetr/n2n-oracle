import os

import dotenv
import solcx
from web3 import Web3, HTTPProvider

from utils.tools import to_address

dotenv.load_dotenv(verbose=True, override=True)

PRIVKEY = os.getenv("PRIVKEY")
MAIN_ADDRESS = to_address(PRIVKEY)

SOLCV = os.getenv("SOLC_VERSION", "0.7.6")
SOLCP = os.getenv("SOLC_PATH", os.getcwd() + "/solcx")
try:
    os.makedirs(SOLCP)
except:
    pass

cnt = 0


def log(net, data):
    global cnt
    cnt += 1
    print(f"#{cnt} [{net}]", data)


def deploy(contract, name, network="LEFT", retry=False):
    web3 = Web3(HTTPProvider(os.getenv(network + "_RPCURL")))

    tx = web3.eth \
        .contract(bytecode=contract["bin"], abi=contract["abi"]) \
        .constructor(os.getenv("VALIDATORS"), os.getenv("THRESHOLD")) \
        .buildTransaction({'gasPrice': web3.eth.gasPrice if retry else int(os.getenv(network + "_GASPRICE")),
                           'nonce': web3.eth.getTransactionCount(MAIN_ADDRESS),
                           'from': MAIN_ADDRESS})

    try:
        signed = web3.eth.account.signTransaction(tx, private_key=PRIVKEY)
        tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
        txr = web3.eth.waitForTransactionReceipt(tx_hash)

        log(network, f"{name} deployed at {txr['contractAddress']}")
        if name == 'Bridge':
            log(network, f"{name} deployed at block {txr['blockHash'].hex()}")
        return txr
    except ValueError as ex:
        if ex.args[0]["message"] == 'transaction underpriced':
            return deploy(contract, name, network, retry=True)
    return None


def main():
    solcx.install_solc(SOLCV, solcx_binary_path=SOLCP)
    solcx.set_solc_version(SOLCV, solcx_binary_path=SOLCP)
    base_dir = "src/contracts/"
    contracts = [("Bridge", "Bridge.sol"), ("Validators Set", "ValidatorSet.sol")]
    res = solcx.compile_files([base_dir + i[1] for i in contracts],
                              optimize=True,
                              optimize_runs=200)

    for net in ["LEFT", "RIGHT"]:
        for name, file in contracts:
            deploy(res.get(f"{base_dir}{file}:{file.removesuffix('.sol')}"), name, net)


if __name__ == '__main__':
    main()
