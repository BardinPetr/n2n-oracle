import pytest
from blockchain_tools import send_transaction_and_check
from helpers import deploy_contracts

from . import US_003


@pytest.mark.it('AC-004-01: Remove one validator.')
@pytest.mark.dependency(depends=US_003, name='AC_004_01', scope='session')
def test_AC_004_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_004_01.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # removeValidator
    send_transaction_and_check(web3_left, accounts[0], \
                               function=validators_set.functions.removeValidator(accounts[3].address))

    # getValidators
    validators = set(validators_set.functions.getValidators().call())

    # Default was 1, 2, 3. Remove 3. Should be 1, 2.
    validators_ = set([accounts[1].address, accounts[2].address])

    assert validators == validators_, \
        f'Validators mismatch:\n{validators} != {validators_}.'


@pytest.mark.it('AC-004-02: Remove does not exist.')
@pytest.mark.dependency(depends=US_003, name='AC_004_02', scope='session')
def test_AC_004_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_004_02.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # removeValidator 4.
    send_transaction_and_check(web3_left, accounts[0], revert=True, \
                               function=validators_set.functions.removeValidator(accounts[4].address))


@pytest.mark.it('AC-004-03: Below the threshold.')
@pytest.mark.dependency(depends=US_003, name='AC_004_03', scope='session')
def test_AC_004_03(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_004_03.')

    default_deployment_environment['THRESHOLD'] = 3

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # removeValidator
    send_transaction_and_check(web3_left, accounts[0], revert=True, \
                               function=validators_set.functions.removeValidator(accounts[3].address))


@pytest.mark.it('AC-004-04: Remove and add again.')
@pytest.mark.dependency(depends=US_003, name='AC_004_04', scope='session')
def test_AC_004_04(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_004_04.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # removeValidator
    send_transaction_and_check(web3_left, accounts[0], \
                               function=validators_set.functions.removeValidator(accounts[3].address))

    # getValidators
    validators = set(validators_set.functions.getValidators().call())

    # Default was 1, 2, 3. Remove 3. Should be 1, 2.
    validators_ = set([accounts[1].address, accounts[2].address])

    assert validators == validators_, \
        f'Validators mismatch:\n{validators} != {validators_}.'

    # addValidator
    send_transaction_and_check(web3_left, accounts[0], \
                               function=validators_set.functions.addValidator(accounts[3].address))

    # getValidators
    validators = set(validators_set.functions.getValidators().call())

    # Was 1, 2. Add 3. Should be 1, 2, 3.
    validators_ = set([accounts[1].address, accounts[2].address, accounts[3].address])

    assert validators == validators_, \
        f'Validators mismatch:\n{validators} != {validators_}.'


@pytest.mark.it('AC-004-05: Remove with bad owner.')
@pytest.mark.dependency(depends=US_003, name='AC_004_05', scope='session')
def test_AC_004_05(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_004_05.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # removeValidator
    send_transaction_and_check(web3_left, accounts[5], revert=True, \
                               function=validators_set.functions.removeValidator(accounts[2].address))
