import json
import pytest

from blockchain_tools import send_transaction_and_check, get_balance, send_transaction
from helpers import deploy_contracts, start_oracle, check_transactions, \
    setLiquidity, exchange_and_check, random_transaction_id

from . import US_009, US_011


@pytest.mark.it('AC-017-01: Reliable token transfer.')
@pytest.mark.dependency(depends = US_009 + US_011, name = 'AC_017_01', scope = 'session')
def test_AC_017_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_017_01.')

    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    

    # ABI.
    with open('./abi/family_1.json') as file:
        family_1_abi = json.load(file)

    with open('./abi/family_2.json') as file:
        family_2_abi = json.load(file)

    # Bytecode.
    with open('./bytecode/family_1.bin') as file:
        family_1_bytecode = file.read()

    with open('./bytecode/family_2.bin') as file:
        family_2_bytecode = file.read()

    # Deploy 1.
    tx_receipt_1 = send_transaction_and_check(web3_left, accounts[5], \
        function = web3_right.eth.contract(\
            abi      = family_1_abi, 
            bytecode = family_1_bytecode).constructor(\
                accounts[6].address, accounts[7].address))

    # Deploy 2.
    tx_receipt_2 = send_transaction_and_check(web3_right, accounts[8], \
        function = web3_right.eth.contract(\
            abi      = family_2_abi, 
            bytecode = family_2_bytecode).constructor(\
                accounts[9].address, accounts[10].address))

    family_1 = web3_right.eth.contract(\
        abi = family_1_abi, address = tx_receipt_1.contractAddress)

    family_2 = web3_right.eth.contract(\
        abi = family_2_abi, address = tx_receipt_2.contractAddress)
    

    # addLiquidity
    send_transaction_and_check(web3_right, accounts[0], \
        function = bridge_right.functions.addLiquidity(), \
        value = web3_right.toWei('100', 'ether'))


    send_transaction_and_check(web3_right, accounts[1], \
        function = bridge_right.functions.commit(\
            family_1.address, web3_right.toWei('50', 'ether'), random_transaction_id()))

    assert web3_right.eth.get_balance(family_1.address) == web3_right.toWei('50', 'ether'), \
        'Destination contract balance mismatch.'

    assert web3_right.eth.get_balance(bridge_right.address) == web3_right.toWei('50', 'ether'), \
        'Bridge contract balance mismatch.'


    send_transaction_and_check(web3_right, accounts[1], \
        function = bridge_right.functions.commit(\
            family_2.address, web3_right.toWei('5', 'ether'), random_transaction_id()))

    assert web3_right.eth.get_balance(family_2.address) == web3_right.toWei('5', 'ether'), \
        'Destination contract balance mismatch.'

    assert web3_right.eth.get_balance(bridge_right.address) == web3_right.toWei('45', 'ether'), \
        'Bridge contract balance mismatch.'