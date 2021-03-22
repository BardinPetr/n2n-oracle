import pytest
from blockchain_tools import send_transaction_and_check
from helpers import deploy_contracts

from . import US_002


@pytest.mark.it('AC-007-01: Setup of upper limit.')
@pytest.mark.dependency(depends=US_002, name='AC_007_01', scope='session')
def test_AC_007_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_007_01.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']

    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit(100000000000000000000))  # 100 ether

    setedLimit = bridge_left.functions.getLiquidityLimit().call()
    assert setedLimit == 100000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit} != {100000000000000000000}.'


@pytest.mark.it('AC-007-02: Change of upper limit.')
@pytest.mark.dependency(depends=US_002, name='AC_007_02', scope='session')
def test_AC_007_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_007_02.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']

    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit(100000000000000000000))  # 100 ether

    setedLimit = bridge_left.functions.getLiquidityLimit().call()
    assert setedLimit == 100000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit} != {100000000000000000000}.'

    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit(150000000000000000000))  # 150 ether

    setedLimit = bridge_left.functions.getLiquidityLimit().call()
    assert setedLimit == 150000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit} != {150000000000000000000}.'


@pytest.mark.it('AC-007-03: Unauthorized setup of upper limit.')
@pytest.mark.dependency(depends=US_002, name='AC_007_03', scope='session')
def test_AC_007_03(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_007_03.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']

    send_transaction_and_check(web3_left, accounts[5], \
                               function=bridge_left.functions.updateLiquidityLimit(
                                   100000000000000000000), revert=True)  # 100 ether
