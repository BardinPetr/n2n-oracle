import os

import solcx
from eth_account import Account


def prepare_solc():
    SOLCV = os.getenv("SOLC_VERSION", "0.7.6")
    SOLCP = os.getenv("SOLC_PATH", os.getcwd() + "/solcx")
    try:
        os.makedirs(SOLCP)
    except:
        pass
    solcx.install_solc(SOLCV, solcx_binary_path=SOLCP)
    solcx.set_solc_version(SOLCV, solcx_binary_path=SOLCP)


def to_address(priv_key):
    prefix = '' if priv_key.startswith('0x') else '0x'
    return Account.privateKeyToAccount(prefix + priv_key).address


def get_ABI(base_dir, contract):
    path = f'{base_dir}{contract}.sol'
    return solcx.compile_files([path],
                               optimize=True,
                               optimize_runs=200)[f"{path}:{contract}"]['abi']
