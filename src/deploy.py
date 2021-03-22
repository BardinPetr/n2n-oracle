import os

import dotenv
import solcx
from web3 import Web3, HTTPProvider

from utils.tools import to_address

dotenv.load_dotenv(verbose=True, override=True)

PRIVKEY = os.getenv("PRIVKEY")
MAIN_ADDRESS = to_address(PRIVKEY)

SOLCV = os.getenv("SOLC_VERSION", "0.7.6")

cnt = 0


def log(net, data):
    global cnt
    cnt += 1
    print(f"#{cnt} [{net}]", data)


def deploy(contract, name, constructor, network="LEFT", retry=False):
    web3 = Web3(HTTPProvider(os.getenv(network + "_RPCURL")))

    tx = web3.eth \
        .contract(bytecode=contract["bin"], abi=contract["abi"]) \
        .constructor(*constructor) \
        .buildTransaction({'gasPrice': web3.eth.gasPrice if retry else int(os.getenv(network + "_GASPRICE")),
                           'nonce': web3.eth.getTransactionCount(MAIN_ADDRESS),
                           'from': MAIN_ADDRESS})

    try:
        signed = web3.eth.account.signTransaction(tx, private_key=PRIVKEY)
        tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
        txr = web3.eth.waitForTransactionReceipt(tx_hash)

        log(network, f"{name} deployed at {txr['contractAddress']}")
        return txr
    except ValueError as ex:
        if ex.args[0]["message"] == 'transaction underpriced':
            return deploy(contract, name, constructor, network, retry=True)
    return None


def main():
    solcx.install_solc(SOLCV)
    solcx.set_solc_version(SOLCV)
    base_dir = "src/contracts/"
    contracts = [("Validators Set", "ValidatorSet.sol"), ("Bridge", "BridgeSide.sol")]
    res = solcx.compile_files([base_dir + i[1] for i in contracts],
                              optimize=True,
                              optimize_runs=200)

    nets = ["LEFT", "RIGHT"]
    br_blocks = []
    for i in nets:
        val = deploy(res.get(f"{base_dir}{contracts[0][1]}:{contracts[0][1].removesuffix('.sol')}"),
                     contracts[0][0],
                     (os.getenv("VALIDATORS").split(), int(os.getenv("THRESHOLD"))),
                     i)['contractAddress']
        br = deploy(res.get(f"{base_dir}{contracts[1][1]}:{contracts[1][1].removesuffix('.sol')}"),
                    contracts[1][0],
                    (val,),
                    i)

        br_blocks.append(br['blockNumber'])

    for i, j in zip(br_blocks, nets):
        log(j, f"Bridge deployed at block {i}")


if __name__ == '__main__':
    main()
