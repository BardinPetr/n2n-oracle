import pytest
from blockchain_tools import send_transaction_and_check, get_balance, send_transaction
from helpers import deploy_contracts, start_oracle, check_transactions, setLiquidity, exchange_and_check

from . import US_012, US_013

@pytest.mark.it('AC-015-01: Simple tokens transfer.')
@pytest.mark.dependency(depends = US_012 + US_013, name='AC_015_01', scope='session')
def test_AC_015_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_015_01.')
    default_deployment_environment['VALIDATORS'] = ' '.join([i.address for i in accounts[1:3]])
    default_deployment_environment['THRESHOLD'] = 1
    result = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)
    val_left = result['left']['validators_set']
    val_right = result['right']['validators_set']
    bridge_right = result['right']['bridge']
    bridge_left = result['left']['bridge']

    setLiquidity(bridge_left, bridge_right, accounts[0], web3_left.toWei('2000', 'ether'))

    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])

    account_1 = accounts[3]
    exchange_and_check(bridge_left, bridge_right, account_1, web3_left.toWei('1000', 'ether'), [accounts[1].address], 1)
    exchange_and_check(bridge_right, bridge_left, account_1, web3_left.toWei('10', 'ether'), [accounts[1].address], 1)




    send_transaction_and_check(web3_left, accounts[0],
                               function=val_left.functions.removeValidator(accounts[1].address),
                               value=0)




    start_balance_3_bridge_right = get_balance(web3_right, bridge_right.address)

    start_balance_4_left = get_balance(web3_left, accounts[11].address)
    start_balance_4_bridge_left = get_balance(web3_left, bridge_left.address)
    block_number = web3_left.eth.block_number + 1

    send_transaction(web3_right, accounts[11], to=bridge_right.address, value=web3_left.toWei('27', 'ether'))

    assert start_balance_3_bridge_right + web3_left.toWei('27', 'ether') == get_balance(web3_right,
                                                                                        bridge_right.address)

    check_transactions(web3_left, [accounts[1].address], block_number, 0)


    assert start_balance_4_left == get_balance(web3_left, accounts[11].address)
    assert start_balance_4_bridge_left == get_balance(web3_left, bridge_left.address)

    start_balance_3_bridge_left = get_balance(web3_left, bridge_left.address)

    start_balance_4_right = get_balance(web3_right, accounts[12].address)
    block_number = web3_right.eth.block_number + 1

    send_transaction(web3_left, accounts[12], to=bridge_left.address, value=web3_left.toWei('42', 'ether'))

    assert start_balance_3_bridge_left + web3_left.toWei('42', 'ether') == get_balance(web3_left, bridge_left.address)

    check_transactions(web3_right, [accounts[1].address], block_number, 1)
    assert start_balance_4_right + web3_left.toWei('42', 'ether') == get_balance(web3_right, accounts[12].address)

    send_transaction_and_check(web3_right, accounts[0],
                               function=val_right.functions.removeValidator(accounts[1].address),
                               value=0)

    start_balance_3_bridge_left = get_balance(web3_left, bridge_left.address)
    start_balance_4_right = get_balance(web3_right, accounts[13].address)
    block_number = web3_right.eth.block_number + 1

    send_transaction(web3_left, accounts[13], to=bridge_left.address, value=web3_left.toWei('15', 'ether'))
    assert start_balance_3_bridge_left + web3_left.toWei('15', 'ether') == get_balance(web3_left, bridge_left.address)
    check_transactions(web3_right, [accounts[1].address], block_number, 0)
    block_number = web3_left.eth.block_number + 2
    send_transaction_and_check(web3_left, accounts[0],
                               function=val_left.functions.addValidator(accounts[1].address),
                               value=0)
    check_transactions(web3_left, [accounts[1].address], block_number, 1)
    assert start_balance_4_left + web3_left.toWei('27', 'ether') == get_balance(web3_left, accounts[11].address)
    block_number = web3_right.eth.block_number + 2
    send_transaction_and_check(web3_right, accounts[0],
                               function=val_right.functions.addValidator(accounts[1].address),
                               value=0)
    check_transactions(web3_right, [accounts[1].address], block_number, 1)
    assert start_balance_4_right + web3_left.toWei('15', 'ether') == get_balance(web3_right, accounts[13].address)
