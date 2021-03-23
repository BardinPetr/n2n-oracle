import pytest

from helpers import deploy_contracts
from blockchain_tools import send_transaction_and_check
from . import US_001


@pytest.mark.it('AC-002-01: Contract registration.')
@pytest.mark.dependency(depends=US_001, name='AC_002_01', scope='session')
def test_AC_002_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_002_01.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    validators_set_left = tmp['left']['validators_set']
    validators_set_right = tmp['right']['validators_set']

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']

    # Default is 1, 2, 3.
    validators = set([accounts[1].address, accounts[2].address, accounts[3].address])
    validators_left = set(validators_set_left.functions.getValidators().call())
    validators_right = set(validators_set_right.functions.getValidators().call())

    assert validators_left == validators, \
        f'Validators mismatch:\n{validators_left} != {validators}.'

    assert validators_right == validators, \
        f'Validators mismatch:\n{validators_right} != {validators}.'

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('100', 'ether'))

    # updateLiquidityLimit
    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.updateLiquidityLimit(web3_left.toWei('100', 'ether')))

    # changeValidatorSet
    send_transaction_and_check(web3_left, accounts[0], \
                               function=bridge_left.functions.changeValidatorSet(accounts[4].address))

    # changeValidatorSet
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.changeValidatorSet(accounts[4].address))
