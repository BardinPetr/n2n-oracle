import pytest
import random
import time
from helpers import deploy_contracts, start_oracle, setLiquidity, check_transactions, exchange_and_check
from blockchain_tools import send_transaction_and_check, check_events

from . import US_012, US_013

@pytest.mark.it('AC-014-01: Several oracles: from left and right')
@pytest.mark.dependency(depends = US_012 + US_013, name = 'AC_014_01', scope = 'session')
def test_AC_014_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_014_01.')
    VALIDATORS = [accounts[1], accounts[2], accounts[3]]
    VALIDATORS_ADDRESSES = list(map(lambda v: v.address, VALIDATORS))

    default_deployment_environment['VALIDATORS'] = ' '.join(map(str, VALIDATORS_ADDRESSES))
    default_deployment_environment['THRESHOLD'] = 2

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']

    ETH_1000 = web3_left.toWei('1000', 'ether')
    setLiquidity(bridge_left, bridge_right, accounts[0], ETH_1000)





    for validator in VALIDATORS:
        start_oracle(log, docker, bridge_left, bridge_right, validator)

    exchange_and_check(bridge_left, bridge_right, accounts[5], \
                       ETH_1000, VALIDATORS_ADDRESSES, 2)

    X = web3_right.toWei(random.randint(1, 50000) / 1000, 'ether')
    exchange_and_check(bridge_right, bridge_left, accounts[5], \
                       X, VALIDATORS_ADDRESSES, 2)

    X = web3_right.toWei(random.randint(1, 50000) / 1000, 'ether')
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
                       X, VALIDATORS_ADDRESSES, 2)



