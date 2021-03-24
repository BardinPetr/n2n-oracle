import pytest

from helpers import deploy_contracts, start_oracle, setLiquidity, check_transactions, exchange_and_check
from blockchain_tools import send_transaction_and_check, check_events
from . import US_010, US_011

@pytest.mark.it('AC-013-01: One oracle: from left and right')
@pytest.mark.dependency(depends = US_010 + US_011, name = 'AC_013_01', scope = 'session')
def test_AC_013_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):
    log.info('Testing AC_013_01.')
    VALIDATORS = [accounts[1]]
    VALIDATORS_ADDRESSES = list(map(lambda v: v.address, VALIDATORS))
    
    default_deployment_environment['VALIDATORS'] = ' '.join(map(str, VALIDATORS_ADDRESSES))
    default_deployment_environment['THRESHOLD'] = len(VALIDATORS_ADDRESSES)
    
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  

    ETH_100 = web3_left.toWei('100', 'ether')
    ETH_10 = web3_left.toWei('10', 'ether')
    ETH_15 = web3_left.toWei('15', 'ether')
    ETH_20 = 2 * ETH_10
    
    setLiquidity(bridge_left, bridge_right, accounts[0], ETH_100)
 
    for validator in VALIDATORS:
        start_oracle(log, docker, bridge_left, bridge_right, validator)
    
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        ETH_100, VALIDATORS_ADDRESSES, 1)

    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        ETH_10, VALIDATORS_ADDRESSES, 1)
    
    exchange_and_check(bridge_right, bridge_left, accounts[7], \
        ETH_15, VALIDATORS_ADDRESSES, 1)
    
    exchange_and_check(bridge_right, bridge_left, accounts[8], \
        ETH_20, VALIDATORS_ADDRESSES, 1)
    
