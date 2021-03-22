import pytest
from blockchain_tools import send_transaction_and_check
from helpers import deploy_contracts

from . import US_004


@pytest.mark.it('AC-005-01: Change threshold.')
@pytest.mark.dependency(depends=US_004, name='AC_005_01', scope='session')
def test_AC_005_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_005_01.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # changeThreshold
    send_transaction_and_check(web3_left, accounts[0], \
                               function=validators_set.functions.changeThreshold(3))

    threshold = validators_set.functions.getThreshold().call()

    assert threshold == 3, \
        f'Threshold mismatch:\n{threshold} != 3.'


@pytest.mark.it('AC-005-02: Threshold more than validators.')
@pytest.mark.dependency(depends=US_004, name='AC_005_02', scope='session')
def test_AC_005_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_005_02.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # changeThreshold
    send_transaction_and_check(web3_left, accounts[0], revert=True, \
                               function=validators_set.functions.changeThreshold(4))


@pytest.mark.it('AC-005-03: Bad owner.')
@pytest.mark.dependency(depends=US_004, name='AC_005_03', scope='session')
def test_AC_005_03(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_005_03.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # changeThreshold
    send_transaction_and_check(web3_left, accounts[5], revert=True, \
                               function=validators_set.functions.changeThreshold(3))
