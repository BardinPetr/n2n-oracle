import pytest
from blockchain_tools import send_transaction_and_check
from helpers import deploy_contracts

from . import US_002


@pytest.mark.it('AC-006-01: Simple add 100 eth.')
@pytest.mark.dependency(depends=US_002, name='AC_006_01', scope='session')
def test_AC_006_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_01.')

    # Take right bridge.
    bridge_right = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['right']['bridge']

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('100', 'ether'))

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Check balance.
    assert balance == web3_right.toWei('100', 'ether'), \
        f'Balance mismatch: {balance} != {web3_right.toWei("100", "ether")}.'

    liquidity = bridge_right.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_right.toWei('100', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_right.toWei("100", "ether")}.'


@pytest.mark.it('AC-006-02: Add 100 eth, then 50 eth more.')
@pytest.mark.dependency(depends=US_002, name='AC_006_02', scope='session')
def test_AC_006_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_02.')

    # Take right bridge.
    bridge_right = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['right']['bridge']

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('100', 'ether'))

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Check balance.
    assert balance == web3_right.toWei('100', 'ether'), \
        f'Balance mismatch: {balance} != {web3_right.toWei("100", "ether")}.'

    liquidity = bridge_right.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_right.toWei('100', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_right.toWei("100", "ether")}.'

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('50', 'ether'))

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Check balance.
    assert balance == web3_right.toWei('150', 'ether'), \
        f'Balance mismatch: {balance} != {web3_right.toWei("150", "ether")}.'

    liquidity = bridge_right.functions.getLiquidityLimit().call()

    # Check liquidity.
    assert liquidity == web3_right.toWei('150', 'ether'), \
        f'Liquidity mismatch: {liquidity} != {web3_right.toWei("150", "ether")}.'


@pytest.mark.it('AC-006-03: Zero value.')
@pytest.mark.dependency(depends=US_002, name='AC_006_03', scope='session')
def test_AC_006_03(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_03.')

    # Take right bridge.
    bridge_right = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['right']['bridge']

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], revert=True, \
                               function=bridge_right.functions.addLiquidity(), \
                               value=0)


@pytest.mark.it('AC-006-04: Bad owner.')
@pytest.mark.dependency(depends=US_002, name='AC_006_04', scope='session')
def test_AC_006_04(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_04.')

    # Take right bridge.
    bridge_right = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['right']['bridge']

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[5], revert=True, \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('100', 'ether'))
