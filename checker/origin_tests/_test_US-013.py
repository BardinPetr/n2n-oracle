import pytest

from helpers import deploy_contracts, start_oracle, setLiquidity, check_transactions
from blockchain_tools import send_transaction_and_check, check_events

@pytest.mark.it('AC-013-01: One oracle: from left and right')
@pytest.mark.dependency(depends = [], name = 'AC_013_01', scope = 'session')
def test_AC_013_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_013_01.')
    
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    setLiquidity(bridge_left, bridge_right, accounts[0], 100)

    start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[10])
    
    ten_eth = web3_left.toWei('10', 'ether')
    
    block_before = web3_right.eth.block_number + 1
    
    send_transaction_and_check(web3_left, accounts[5],
                               to=bridge_left.address,
                               value=ten_eth,
                               )
    
    check_transactions(web3_right, accounts[10].address, block_before, 1)
    
    assert web3_right.eth.get_balance(accounts[5].address) == ten_eth

