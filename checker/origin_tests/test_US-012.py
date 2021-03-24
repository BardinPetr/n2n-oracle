import pytest

from helpers import deploy_contracts, start_oracle, setLiquidity, exchange_and_check
from blockchain_tools import send_transaction_and_check

from . import US_008, US_009

@pytest.mark.it('AC-012-01: Exchange tokens.')
@pytest.mark.dependency(depends = US_008 + US_009, name = 'AC_012_01', scope = 'session')
def test_AC_012_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_012_01.')
    
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], web3_left.toWei('100', 'ether'))

    # Oracle with accounts[10].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('10', 'ether'), set([accounts[1].address]), 1)  

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[6], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 1)   

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('20', 'ether'), set([accounts[1].address]), 1)


@pytest.mark.it('AC-012-02: Exchange tokens before oracle start.')
@pytest.mark.dependency(depends = US_008 + US_009, name = 'AC_012_02', scope = 'session')
def test_AC_012_02(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_012_02.')
    
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], web3_left.toWei('100', 'ether'))

    def before_check_callback() -> None:
        # Oracle with accounts[10].
        start_oracle(log, docker, bridge_left, bridge_right, accounts[1])

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('10', 'ether'), set([accounts[1].address]), \
            1, before_check_callback = before_check_callback, timeout = 30)