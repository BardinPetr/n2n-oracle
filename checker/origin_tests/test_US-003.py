import pytest
from blockchain_tools import send_transaction_and_check
from helpers import deploy_contracts

from . import US_002


@pytest.mark.it('AC-003-01: Addition of a validator.')
@pytest.mark.dependency(depends=US_002, name='AC_003_01', scope='session')
def test_AC_003_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_003_01.')

    validators = set(default_deployment_environment['VALIDATORS'].split())
    default_deployment_environment['VALIDATORS'] = ' '.join([i.address for i in accounts[1:3]])
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)
    validators_set_left = tmp['left']['validators_set']

    # addValidator
    send_transaction_and_check(web3_left, accounts[0], \
                               function=validators_set_left.functions.addValidator(accounts[3].address))

    validators_left = set(validators_set_left.functions.getValidators().call())

    assert validators == validators_left, \
        f'Validators mismatch:\n{validators_left} != {validators}.'


@pytest.mark.it('AC-003-02: Adding of an existed validator.')
@pytest.mark.dependency(depends=US_002, name='AC_003_02', scope='session')
def test_AC_003_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_003_02.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # add existed validator.
    send_transaction_and_check(web3_left, accounts[0], revert=True, \
                               function=validators_set.functions.addValidator(accounts[1].address))


@pytest.mark.it('AC-003-03: Unauthorized addition of a validator.')
@pytest.mark.dependency(depends=US_002, name='AC_003_03', scope='session')
def test_AC_003_03(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_003_02.')

    # Take left set.
    validators_set = \
        deploy_contracts(docker, log, web3_left, \
                         web3_right, default_deployment_environment)['left']['validators_set']

    # add existed validator.
    send_transaction_and_check(web3_left, accounts[4], revert=True, \
                               function=validators_set.functions.addValidator(accounts[1].address))
