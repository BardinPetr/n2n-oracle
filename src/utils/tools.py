import os

import dotenv
import solcx
from eth_account import Account


def install_solc():
    try:
        dotenv.load_dotenv(verbose=True, override=True)
        SOLCV = os.getenv("SOLC_VERSION", "0.7.6")
        solcx.install_solc(SOLCV)
        solcx.set_solc_version(SOLCV)
    except:
        install_solc()


def to_address(priv_key):
    prefix = '' if priv_key.startswith('0x') else '0x'
    return Account.privateKeyToAccount(prefix + priv_key).address


def get_ABI(base_dir, contract):
    path = f'{base_dir}{contract}.sol'
    return solcx.compile_files([path],
                               optimize=True,
                               optimize_runs=200)[f"{path}:{contract}"]['abi']
