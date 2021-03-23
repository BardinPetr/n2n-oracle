import pytest
from blockchain_tools import send_transaction_and_check, get_balance
from helpers import deploy_contracts, random_transaction_id

from . import US_006


@pytest.mark.it('AC-009-01: 1 of 1 validators.')
@pytest.mark.dependency(depends=US_006, name='AC_009_01', scope='session')
def test_AC_009_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_01.')
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1
    bridge_right = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)['right'][
        'bridge']

    send_transaction_and_check(web3_right, accounts[1], revert=True,
                               function=bridge_right.functions.commit(accounts[2].address,
                                                                      web3_right.toWei('50', 'ether'),
                                                                      random_transaction_id()))

    send_transaction_and_check(web3_right, accounts[0],
                               function=bridge_right.functions.addLiquidity(),
                               value=web3_right.toWei('100', 'ether'))

    assert bridge_right.functions.getLiquidityLimit().call() == web3_right.toWei('100', 'ether')
    start_balance = get_balance(web3_right, accounts[2].address)
    send_transaction_and_check(web3_right, accounts[1], function=bridge_right.functions.commit(accounts[2].address,
                                                                                               web3_right.toWei('50',
                                                                                                                'ether'),
                                                                                               random_transaction_id()),
                               value=0)

    assert get_balance(web3_right, accounts[2].address) == start_balance + web3_right.toWei('50', 'ether')
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('50', 'ether')
    assert bridge_right.functions.getLiquidityLimit().call() == web3_right.toWei('50', 'ether')
    send_transaction_and_check(web3_right, accounts[1], revert=True,
                               function=bridge_right.functions.commit(accounts[2].address,
                                                                      web3_right.toWei('51', 'ether'),
                                                                      random_transaction_id()))
    start_balance = get_balance(web3_right, accounts[3].address)
    send_transaction_and_check(web3_right, accounts[1], function=bridge_right.functions.commit(accounts[3].address,
                                                                                               web3_right.toWei('5',
                                                                                                                'ether'),
                                                                                               random_transaction_id()),
                               value=0)
    assert get_balance(web3_right, accounts[3].address) == start_balance + web3_right.toWei('5', 'ether')
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('45', 'ether')
    assert bridge_right.functions.getLiquidityLimit().call() == web3_right.toWei('45', 'ether')
    send_transaction_and_check(web3_right, accounts[0], revert=True,
                               function=bridge_right.functions.commit(accounts[4].address,
                                                                      web3_right.toWei('5', 'ether'),
                                                                      random_transaction_id()))
    start_balance = get_balance(web3_right, accounts[3].address)
    tx_hash = random_transaction_id()
    send_transaction_and_check(web3_right, accounts[1], function=bridge_right.functions.commit(accounts[3].address,
                                                                                               web3_right.toWei('5',
                                                                                                                'ether'),
                                                                                               tx_hash), value=0)
    assert get_balance(web3_right, accounts[3].address) == start_balance + web3_right.toWei('5', 'ether')
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('40', 'ether')
    assert bridge_right.functions.getLiquidityLimit().call() == web3_right.toWei('40', 'ether')
    send_transaction_and_check(web3_right, accounts[1], revert=True,
                               function=bridge_right.functions.commit(accounts[3].address,
                                                                      web3_right.toWei('5',
                                                                                       'ether'),
                                                                      tx_hash), value=0)


@pytest.mark.it('AC-009-02: N of M validators')
@pytest.mark.dependency(depends=US_006, name='AC_009_02', scope='session')
def test_AC_009_02(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_006_02.')
    bridge_right = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)['right'][
        'bridge']
    send_transaction_and_check(web3_right, accounts[0],
                               function=bridge_right.functions.addLiquidity(),
                               value=web3_right.toWei('100', 'ether'))
    start_balance_1 = get_balance(web3_right, accounts[5].address)
    tx_hash_1 = random_transaction_id()
    send_transaction_and_check(web3_right, accounts[2], function=bridge_right.functions.commit(accounts[5].address,
                                                                                               web3_right.toWei('50',
                                                                                                                'ether'),
                                                                                               tx_hash_1
                                                                                               ), value=0)
    assert start_balance_1 == get_balance(web3_right, accounts[5].address)
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('100', 'ether')
    send_transaction_and_check(web3_right, accounts[2], revert=True,
                               function=bridge_right.functions.commit(accounts[5].address,
                                                                      web3_right.toWei('50',
                                                                                       'ether'),
                                                                      tx_hash_1
                                                                      ), value=0)
    tx_hash_2 = random_transaction_id()
    start_balance_2 = get_balance(web3_right, accounts[6].address)
    send_transaction_and_check(web3_right, accounts[2], function=bridge_right.functions.commit(accounts[6].address,
                                                                                               web3_right.toWei('15',
                                                                                                                'ether'),
                                                                                               tx_hash_2
                                                                                               ), value=0)
    assert start_balance_2 == get_balance(web3_right, accounts[6].address)
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('100', 'ether')
    send_transaction_and_check(web3_right, accounts[3], function=bridge_right.functions.commit(accounts[5].address,
                                                                                               web3_right.toWei('50',
                                                                                                                'ether'),
                                                                                               tx_hash_1
                                                                                               ), value=0)
    assert start_balance_1 + web3_right.toWei('50', 'ether') == get_balance(web3_right, accounts[5].address)
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('50', 'ether')
    send_transaction_and_check(web3_right, accounts[1], function=bridge_right.functions.commit(accounts[6].address,
                                                                                               web3_right.toWei('15',
                                                                                                                'ether'),
                                                                                               tx_hash_2
                                                                                               ), value=0)
    assert start_balance_2 + web3_right.toWei('15', 'ether') == get_balance(web3_right, accounts[6].address)
    assert get_balance(web3_right, bridge_right.address) == web3_right.toWei('35', 'ether')
    send_transaction_and_check(web3_right, accounts[3], revert=True,
                               function=bridge_right.functions.commit(accounts[6].address,
                                                                      web3_right.toWei('15',
                                                                                       'ether'),
                                                                      tx_hash_2
                                                                      ), value=0)
