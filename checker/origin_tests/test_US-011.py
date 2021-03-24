import pytest
from blockchain_tools import send_transaction_and_check, check_events, get_balance
from helpers import deploy_contracts, random_transaction_id
from web3 import Web3

from . import US_007


@pytest.mark.it('AC-011-01: 1 of 1 validators.')
@pytest.mark.dependency(depends=US_007, name='AC_011_01', scope='session')
def test_AC_011_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_011_01.')

    validators = set(default_deployment_environment['VALIDATORS'].split())
    default_deployment_environment['VALIDATORS'] = str(accounts[1].address)
    default_deployment_environment['THRESHOLD'] = 1

    # Left right bridge.
    bridge_left = deploy_contracts(
        docker, log, web3_left,
        web3_right, default_deployment_environment
    )['left']['bridge']

    args_for_commit = (accounts[4].address, Web3.toWei('50', 'ether'), random_transaction_id())

    # commit to left
    send_transaction_and_check(web3_left, accounts[1], revert=True, \
                               function=bridge_left.functions.commit(*args_for_commit))

    liqLimit = Web3.toWei('100', 'ether')

    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit(liqLimit))
    assert bridge_left.functions.getLiquidityLimit().call() == liqLimit

    send_transaction_and_check(web3_left, accounts[1], revert=True, \
                               function=bridge_left.functions.commit(*args_for_commit))

    bridge_action_initiated = \
        bridge_left.events.bridgeActionInitiated().createFilter(fromBlock='latest')

    send_transaction_and_check(web3_left, accounts[5],
                               to=bridge_left.address,
                               value=Web3.toWei('75', 'ether'),
                               )

    balance = web3_left.eth.get_balance(bridge_left.address)

    # Check balance.
    assert balance == web3_left.toWei('75', 'ether'), \
        f'Contract balance mismatch: {balance} != {web3_left.toWei("75", "ether")}.'

    # bridgeActionInitiated
    check_events(bridge_action_initiated, \
                 {'recipient': accounts[5].address, 'amount': web3_left.toWei("75", "ether")})

    liquidity = bridge_left.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_left.toWei('25', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_left.toWei("25", "ether")}.'

    balance_before = web3_left.eth.get_balance(args_for_commit[0])

    send_transaction_and_check(web3_left, accounts[1], \
                               function=bridge_left.functions.commit(*args_for_commit))

    assert balance_before + args_for_commit[1] == web3_left.eth.get_balance(args_for_commit[0])

    assert bridge_left.functions.getLiquidityLimit().call() == web3_left.toWei("75", "ether")

    args_for_commit = (accounts[4].address, Web3.toWei('26', 'ether'), random_transaction_id())
    send_transaction_and_check(web3_left, accounts[1], revert=True, \
                               function=bridge_left.functions.commit(*args_for_commit))

    args_for_commit = (accounts[4].address, Web3.toWei('5', 'ether'), random_transaction_id())

    balance_before = web3_left.eth.get_balance(args_for_commit[0])

    send_transaction_and_check(web3_left, accounts[1], \
                               function=bridge_left.functions.commit(*args_for_commit))

    assert balance_before + args_for_commit[1] == web3_left.eth.get_balance(args_for_commit[0])

    assert bridge_left.functions.getLiquidityLimit().call() == web3_left.toWei("80", "ether")

    args_for_commit = (accounts[5].address, Web3.toWei('5', 'ether'), random_transaction_id())
    send_transaction_and_check(web3_left, accounts[4], revert=True, \
                               function=bridge_left.functions.commit(*args_for_commit))

    args_for_commit = (accounts[4].address, Web3.toWei('5', 'ether'), random_transaction_id())

    balance_before = web3_left.eth.get_balance(args_for_commit[0])

    send_transaction_and_check(web3_left, accounts[1], \
                               function=bridge_left.functions.commit(*args_for_commit))

    assert balance_before + args_for_commit[1] == web3_left.eth.get_balance(args_for_commit[0])

    send_transaction_and_check(web3_left, accounts[1], revert=True, \
                               function=bridge_left.functions.commit(*args_for_commit))


@pytest.mark.it('AC-011-02: N of M validators.')
@pytest.mark.dependency(depends=US_007, name='AC_011_02', scope='session')
def test_AC_011_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_011_02.')
    bridge_right = deploy_contracts(
        docker, log, web3_left,
        web3_right, default_deployment_environment
    )['right']['bridge']
    validators = accounts[1:4]

    send_transaction_and_check(web3_right, accounts[0],
                               function=bridge_right.functions.addLiquidity(),
                               value=web3_right.toWei('100', 'ether'))

    account_1 = accounts[4]
    tx_hash_1 = random_transaction_id()
    start_balance = get_balance(web3_right, account_1.address)
    send_transaction_and_check(web3_right, validators[1], function=bridge_right.functions.commit(account_1.address,
                                                                                                 web3_right.toWei('50',
                                                                                                                  'ether'),
                                                                                                 tx_hash_1),
                               value=0)
    assert get_balance(web3_right, account_1.address) == start_balance
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('100', 'ether')
    send_transaction_and_check(web3_right, validators[1], revert=True,
                               function=bridge_right.functions.commit(account_1.address,
                                                                      web3_right.toWei('50',
                                                                                       'ether'),
                                                                      tx_hash_1),
                               value=0)
    account_2 = accounts[5]
    tx_hash_2 = random_transaction_id()
    start_balance_1 = get_balance(web3_right, account_2.address)
    send_transaction_and_check(web3_right, validators[1], function=bridge_right.functions.commit(account_2.address,
                                                                                                 web3_right.toWei('15',
                                                                                                                  'ether'),
                                                                                                 tx_hash_2),
                               value=0)
    send_transaction_and_check(web3_right, validators[2], function=bridge_right.functions.commit(account_1.address,
                                                                                                 web3_right.toWei('50',
                                                                                                                  'ether'),
                                                                                                 tx_hash_1),
                               value=0)
    assert get_balance(web3_right, account_1.address) == start_balance + web3_right.toWei('50', 'ether')
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('50', 'ether')
    send_transaction_and_check(web3_right, validators[0], function=bridge_right.functions.commit(account_2.address,
                                                                                                 web3_right.toWei('15',
                                                                                                                  'ether'),
                                                                                                 tx_hash_2),
                               value=0)
    assert get_balance(web3_right, account_2.address) == start_balance_1 + web3_right.toWei('15', 'ether')
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('35', 'ether')
    send_transaction_and_check(web3_right, validators[2], revert=True,
                               function=bridge_right.functions.commit(account_2.address,
                                                                      web3_right.toWei('15',
                                                                                       'ether'),
                                                                      tx_hash_2),
                               value=0)
