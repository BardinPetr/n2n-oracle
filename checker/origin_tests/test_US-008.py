import pytest
from blockchain_tools import send_transaction_and_check, check_events
from helpers import deploy_contracts

from . import US_007


@pytest.mark.it('AC-008-01: Send token to bridge left.')
@pytest.mark.dependency(depends=US_007, name='AC_008_01', scope='session')
def test_AC_008_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_008_01.')

    # Take left bridge.
    bridge_left = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['bridge']

    log.info(bridge_left.functions.getLiquidityLimit().call())

    # Send token. No liquidity.
    send_transaction_and_check(web3_left, accounts[5], revert=True, \
                               to=bridge_left.address,
                               value=web3_left.toWei('50', 'ether'))

    # updateLiquidityLimit
    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit( \
                                   web3_left.toWei('100', 'ether')))

    # Event.
    bridge_action_initiated = \
        bridge_left.events.bridgeActionInitiated().createFilter(fromBlock='latest')

    # Send token.
    send_transaction_and_check(web3_left, accounts[5], \
                               to=bridge_left.address,
                               value=web3_left.toWei('50', 'ether'))

    balance = web3_left.eth.get_balance(bridge_left.address)

    # Check balance.
    assert balance == web3_left.toWei('50', 'ether'), \
        f'Contract balance mismatch: {balance} != {web3_left.toWei("50", "ether")}.'

    # bridgeActionInitiated
    check_events(bridge_action_initiated, \
                 {'recipient': accounts[5].address, 'amount': web3_left.toWei("50", "ether")})

    liquidity = bridge_left.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_left.toWei('50', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_left.toWei("50", "ether")}.'

    # Send token.
    send_transaction_and_check(web3_left, accounts[6], \
                               to=bridge_left.address,
                               value=web3_left.toWei('40', 'ether'))

    balance = web3_left.eth.get_balance(bridge_left.address)

    # Check balance.
    assert balance == web3_left.toWei('90', 'ether'), \
        f'Contract balance mismatch: {balance} != {web3_left.toWei("90", "ether")}.'

    # bridgeActionInitiated
    check_events(bridge_action_initiated, \
                 {'recipient': accounts[6].address, 'amount': web3_left.toWei("40", "ether")})

    liquidity = bridge_left.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_left.toWei('10', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_left.toWei("10", "ether")}.'

    # Send token.
    send_transaction_and_check(web3_left, accounts[6], \
                               to=bridge_left.address,
                               value=web3_left.toWei('5', 'ether'))

    balance = web3_left.eth.get_balance(bridge_left.address)

    # Check balance.
    assert balance == web3_left.toWei('95', 'ether'), \
        f'Contract balance mismatch: {balance} != {web3_left.toWei("95", "ether")}.'

    # bridgeActionInitiated
    check_events(bridge_action_initiated, \
                 {'recipient': accounts[6].address, 'amount': web3_left.toWei("5", "ether")})

    liquidity = bridge_left.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_left.toWei('5', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_left.toWei("5", "ether")}.'

    # Send token.
    send_transaction_and_check(web3_left, accounts[6], revert=True, \
                               to=bridge_left.address,
                               value=web3_left.toWei('10', 'ether'))

    # updateLiquidityLimit
    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit( \
                                   web3_left.toWei('15', 'ether')))

    # Send token.
    send_transaction_and_check(web3_left, accounts[6], \
                               to=bridge_left.address,
                               value=web3_left.toWei('10', 'ether'))

    balance = web3_left.eth.get_balance(bridge_left.address)

    # Check balance.
    assert balance == web3_left.toWei('105', 'ether'), \
        f'Contract balance mismatch: {balance} != {web3_left.toWei("105", "ether")}.'

    # bridgeActionInitiated
    check_events(bridge_action_initiated, \
                 {'recipient': accounts[6].address, 'amount': web3_left.toWei("10", "ether")})

    liquidity = bridge_left.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_left.toWei('5', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_left.toWei("5", "ether")}.'

    # Send token.
    send_transaction_and_check(web3_left, accounts[6], revert=True, \
                               to=bridge_left.address,
                               value=web3_left.toWei('10', 'ether'))
