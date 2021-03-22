import os
import time
import pytest

from docker import DockerClient

from logging import Logger, getLogger

from web3            import Web3, Account
from web3.eth        import Contract
from web3.middleware import geth_poa_middleware

from requests.exceptions import ConnectionError

from helpers          import stop_oracle
from docker_tools     import start_container, stop_container
from blockchain_tools import send_transaction_and_check


@pytest.fixture(scope = 'session')
def log() -> Logger:
    return getLogger('ftchecker')

@pytest.fixture(scope = 'session')
def docker() -> DockerClient:
    return DockerClient()


@pytest.fixture(scope = 'session')
def web3_left() -> Web3:
    web3 = Web3(Web3.HTTPProvider('http://geth-left:8545'))
    
    web3.middleware_onion.inject(geth_poa_middleware, layer = 0)
    
    return web3

@pytest.fixture(scope = 'session')
def web3_right() -> Web3:
    web3 = Web3(Web3.HTTPProvider('http://geth-right:8545'))
    
    web3.middleware_onion.inject(geth_poa_middleware, layer = 0)
    
    return web3


@pytest.fixture(scope = 'session')
def accounts() -> list[Account]:
    # Empty web3.
    web3 = Web3()

    # Empty accounts. Will be filled, web can be any.
    return [web3.eth.account.from_key(web3.keccak(os.urandom(32))) for i in range(20)]
        

@pytest.fixture(scope = 'function', autouse = True)
def setup_teardown(log:Logger, accounts:list[Account]) -> None:
    # To be removed after test.
    pytest.oracles = []
    
    yield None

    # Stop all possible oracles. Oracles can from 10.
    for address in pytest.oracles:
        stop_oracle(log, address, remove_db = True)


@pytest.fixture(scope = 'session', autouse = True)
def nodes(web3_left:Web3, web3_right:Web3, accounts:list[Account], docker:DockerClient, \
    log:Logger, request) -> None:

    def start_geth(name:str, period:int):
        entrypoint = [
            'geth',
            '--dev',
            '--dev.period', str(period),

            '--nousb',

            '--rpc.gascap', '0',
            '--rpc.txfeecap', '0',

            '--miner.gasprice', '20000000000',
            '--miner.gaslimit', '12500000',

            '--verbosity', '2',
            '--ipcdisable',

            '--http',
            '--http.addr', '0.0.0.0',
            '--http.port', '8545',

            '--http.corsdomain', '*',
            '--http.vhosts',     '*',

            '--http.api', 'web3,eth,miner'
        ]

        return start_container(docker, 'ethereum/client-go:v1.9.25', log, \
            entrypoint = entrypoint, name = name)
    
    def initialize_accounts():
        # Send.
        for i in range(len(accounts)):
            account = accounts[i]

            # Left.
            web3_left.eth.sendTransaction(
                {
                    'from':  web3_left.eth.coinbase, 
                    'to':    account.address,
                    'value': Web3.toWei('1000000', 'ether')
                }
            )

            # Right.
            web3_right.eth.sendTransaction(
                {
                    'from':  web3_right.eth.coinbase, 
                    'to':    account.address,
                    'value': Web3.toWei('1000000', 'ether')
                }
            )

            # Check balances.
            balance_src = Web3.fromWei(web3_left.eth.get_balance(account.address), 'ether')
            balance_dst = Web3.fromWei(web3_right.eth.get_balance(account.address), 'ether')

            log.debug(f'Account (i): {account.address}: {balance_src} {balance_dst}.')

        # Burn other.
        web3_left.eth.sendTransaction(
            {
                'from':  web3_left.eth.coinbase, 
                'to':    web3_left.toChecksumAddress(Web3.keccak(os.urandom(32)).hex()[:42]),
                'value': int(web3_left.eth.get_balance(web3_left.eth.coinbase) - Web3.toWei('0.005', 'ether'))
            }
        )

        # Burn other.
        web3_right.eth.sendTransaction(
            {
                'from':  web3_right.eth.coinbase, 
                'to':    web3_right.toChecksumAddress(Web3.keccak(os.urandom(32)).hex()[:42]),
                'value': int(web3_right.eth.get_balance(web3_right.eth.coinbase) - Web3.toWei('0.005', 'ether'))
            }
        )
        
        # To be different contract addresses.
        send_transaction_and_check(web3_left, accounts[0], \
            to = accounts[9].address, value = 12345678)

        return accounts

    if hasattr(request, 'param'):
        period = request.param

    else:
        # Instant mine.
        period = 0
    try:
        stop_container(docker, 'geth-left', log)
        stop_container(docker, 'geth-right', log)
    except:
        pass

    start_geth('geth-left',  period)
    start_geth('geth-right', period)

    # Wait hosts up.
    for i in range(15):
        try:
            web3_left.eth.block_number
            web3_right.eth.block_number

        except ConnectionError:
            time.sleep(1)

    # Deposit accounts.
    initialize_accounts()

    yield None
    
    # Teardown.
    stop_container(docker, 'geth-left',  log)
    stop_container(docker, 'geth-right', log)

@pytest.fixture(scope = 'function')
def default_deployment_environment(web3_left:Web3, web3_right:Web3, accounts:list[Account]):
    return {
        # Owner 0 by default.
        'PRIVKEY': accounts[0]._private_key.hex(),
        'LEFT_RPCURL': web3_left.manager._provider.endpoint_uri,
        'RIGHT_RPCURL': web3_right.manager._provider.endpoint_uri,
        'LEFT_GASPRICE': '20000000000',
        'RIGHT_GASPRICE': '20000000000',
        # Validator 1, 2, 3 by default.
        'VALIDATORS': ' '.join([i.address for i in accounts[1:4]]),
        'THRESHOLD': 2
    }