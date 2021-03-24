import pytest
import random
import time
from helpers import deploy_contracts, start_oracle, setLiquidity, check_transactions, exchange_and_check
from blockchain_tools import send_transaction_and_check, check_events

from . import US_014, US_018

@pytest.mark.it('AC-019-01: Several oracles: from left and right')
@pytest.mark.dependency(depends = US_014 + US_018, name='AC_019_01', scope='session')
def test_AC_019_01(docker, log, web3_left, web3_right, accounts, \
                   default_deployment_environment):
    log.info('Testing AC_019_01.')
    
    VALIDATORS = [accounts[1], accounts[2], accounts[3]]
    VALIDATORS_ADDRESSES = list(map(lambda v: v.address, VALIDATORS))

    default_deployment_environment['VALIDATORS'] = ' '.join(map(str, VALIDATORS_ADDRESSES))
    default_deployment_environment['THRESHOLD'] = 2

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']
    send_transaction_and_check(web3_left, accounts[0],
                               function=bridge_left.functions.enableRobustMode())
    send_transaction_and_check(web3_right, accounts[0],
                               function=bridge_right.functions.enableRobustMode())
    ETH_1000 = web3_left.toWei('1000', 'ether')
    setLiquidity(bridge_left, bridge_right, accounts[0], ETH_1000 * 2)

    for validator in VALIDATORS:
        start_oracle(log, docker, bridge_left, bridge_right, validator)

    exchange_and_check(bridge_left, bridge_right, accounts[5], \
                       ETH_1000, VALIDATORS_ADDRESSES, 2)

    assert web3_right.eth.get_balance(bridge_right.address) == ETH_1000, \
        f'Right contract should have 1000 eth balance, but {web3_right.eth.get_balance(bridge_right.address)}.'

    X = web3_right.toWei(random.randint(1, 50000) / 1000, 'ether')
    
    # Save balance.
    balance_right = web3_right.eth.get_balance(accounts[5].address)
    # Save balance.
    balance_left = web3_left.eth.get_balance(accounts[5].address)

    # Save balance.
    balance_right_bridge = web3_right.eth.get_balance(bridge_right.address)
    # Save balance.
    balance_left_bridge = web3_left.eth.get_balance(bridge_left.address)


    start_block_left = web3_left.eth.block_number
    start_block_right = web3_right.eth.block_number

    # Events.
    commits_collected_event = \
        bridge_right.events.commitsCollected.createFilter(fromBlock = 'latest')

    # Save block.
    block = web3_right.eth.block_number

    # Send X. from right to left.
    send_transaction_and_check(web3_right, accounts[5], \
        to = bridge_right.address, 
        value = X)


    block = web3_right.eth.get_block(block + 1)

    assert len(block.transactions) == 1, \
        f'To much txs in block: {len(block.transactions)}'

    # Tx.
    tx_hash = block.transactions[0]

    # Balance changes.
    assert web3_right.eth.get_balance(accounts[5].address) <= balance_right - X, \
        f'Right user balance mismatch: {web3_right.eth.get_balance(accounts[5].address)} > {balance_right - X}.'

    # Balance changes.
    assert web3_right.eth.get_balance(bridge_right.address) == balance_right_bridge + X, \
        f'Right contract balance mismatch: {web3_right.eth.get_balance(bridge_right.address)} != {balance_right_bridge + X}.'


    # Wait txs
    time.sleep(15)

    finish_block_left = web3_left.eth.block_number
    finish_block_right = web3_right.eth.block_number

    # Right tx.
    assert 3 <= (finish_block_right - start_block_right) <= 4, \
        f'Too much or too low transaction in right chain: {finish_block_right - start_block_right}.'

    # Left tx.
    assert (finish_block_left - start_block_left) == 1, \
        f'To much txs in left chain: {finish_block_left - start_block_left}.'

    # Event.
    check_events(commits_collected_event, {'id': tx_hash, 'commits': 2})

    # Balance changes.
    assert web3_left.eth.get_balance(accounts[5].address) == balance_left + X, \
        f'Left user balance mismatch: {web3_left.eth.get_balance(accounts[5].address)} != {balance_left + X}.'

    # Balance changes.
    assert web3_left.eth.get_balance(bridge_left.address) == balance_left_bridge - X, \
        f'Left contract balance mismatch: {web3_left.eth.get_balance(bridge_left.address)} != {balance_left_bridge - X}.'


    Y = web3_right.toWei(random.randint(1, 50000) / 1000, 'ether')
    
    # From left to right.
    exchange_and_check(bridge_left, bridge_right, accounts[6], \
                       Y, VALIDATORS_ADDRESSES, 2)
