import pytest

from helpers import deploy_contracts, start_oracle, setLiquidity, check_transactions
from blockchain_tools import send_transaction_and_check, check_events


@pytest.mark.it('AC-014-01: Several oracles: from left and right')
@pytest.mark.dependency(depends = [], name = 'AC_014_01', scope = 'session')
def test_AC_014_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_014_01.')
    
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    setLiquidity(bridge_left, bridge_right, accounts[0], 1000)

    start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[10])
    start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[11])
    start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[12])

    start_block = web3_right.block_number()
    start_balance = web3_right.get_balnce(accounts[5].address)
    send_transaction_and_check(web3_right, accounts[5],
                               value=web3_left.toWei(1000, 'ether'), to=bridge_left.address, revert=False)
    check_transactions(web3_right, set(accounts[10].address, accounts[11].address, accounts[12].address), start_block, count=2)
    final_balance = web3_right.get_balnce(accounts[5].address)
    assert start_balance + web3_right.toWei(1000, 'ether') == final_balance, \
        f'Wrong balance:\n{accounts[5].address} balance didnt increase.'

    start_block = web3_left.block_number()
    start_balance = web3_left.get_balnce(accounts[6].address)
    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_left.toWei(10, 'ether'), to=bridge_right.address, revert=False)
    check_transactions(web3_left, set(accounts[10].address, accounts[11].address, accounts[12].address), start_block, count=2)
    final_balance = web3_left.get_balnce(accounts[6].address)
    assert start_balance + web3_left.toWei(10, 'ether') == final_balance, \
        f'Wrong balance:\n{accounts[6].address} balance didnt increase.'




    #start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[10])
    #start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[11])
    #start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[12])
    

    