import sys
import dotenv
import logging
import os
import json
from ..src.utils.tools import get_ABI
from ..src.utils.contract_wrapper import ContractWrapper
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware


def create(x):
    w = Web3(HTTPProvider(os.getenv(x + '_RPCURL')))
    w.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w


dotenv.load_dotenv(verbose=True, override=True)
logging.basicConfig(level=logging.INFO)

priv_key = os.getenv('PRIVKEY')

contract_addr = (os.getenv('LEFT_ADDRESS'), os.getenv('RIGHT_ADDRESS'))
gas = (int(os.getenv('LEFT_GASPRICE')), int(os.getenv('RIGHT_GASPRICE')))

web3 = [create(i) for i in ['LEFT', 'RIGHT']]

abi_path = 'src/contracts/abi.json'
abi = None

try:
    with open(abi_path) as f:
        abi = json.load(f)
except:
    abi = get_ABI('src/contracts/', 'BridgeSide')
    json.dump(abi, open(abi_path, 'w'))

contract_left, contract_right = [
    ContractWrapper(w3=web3[i], gas_price=gas[i], user_pk=priv_key, abi=abi, address=contract_addr[i])
    for i in range(len(contract_addr))
]

if __name__ == '__main__':
    if len(sys.argv) > 1:
        tx_hash = sys.argv[1]
        recipient, amount = contract_right.getTransferDetails(tx_hash)
        r_list, s_list, v_list = [], [], []
        for i in range(len(os.getenv('VALIDATORS').split())):
            r, s, v = contract_right.getCommit(tx_hash, i)
            r_list.append(r)
            s_list.append(s)
            v_list.append(v)
        contract_left.applyCommits(recipient, amount, tx_hash, r_list, s_list, v_list)
        print(tx_hash, 'executed')
