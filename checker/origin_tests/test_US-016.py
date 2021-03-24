import pytest

from helpers import deploy_contracts, start_oracle, stop_oracle, \
    setLiquidity, exchange_and_check
    
from blockchain_tools import send_transaction_and_check

from . import US_012, US_013

@pytest.mark.it('AC-016-01: Send while oracles down.')
@pytest.mark.dependency(depends = US_012 + US_013, name = 'AC_016_01', scope = 'session')
def test_AC_016_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_016_01.')
    
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])


    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), set([accounts[1].address]), 1)  
    
    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1000.
    assert balance == web3_left.toWei('1000', 'ether'), \
        f'Right bridge has non zero balande: {balanse}.'


    # Exchange.
    exchange_and_check(bridge_right, bridge_left, accounts[5], \
        web3_left.toWei('10', 'ether'), set([accounts[1].address]), 1)   

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1010.
    assert balance == web3_left.toWei('1010', 'ether'), \
        f'Right bridge has bad balande: {balanсe} != {web3_left.toWei("1010", "ether")}.'


    # $ docker-compose down.
    stop_oracle(log, docker, accounts[1].address)



    # Exchange. No transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[1].address]), 0)

    

    # Exchange. No transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 0)


    state_1 = {
        'block_dst': bridge_left.web3.eth.block_number + 1,
        'balance_dst': web3_left.eth.get_balance(accounts[6].address),
        'contract_dst': web3_left.eth.get_balance(bridge_left.address)
    }

    state_2 = {
        'block_dst': bridge_right.web3.eth.block_number + 1,
        'balance_dst': web3_right.eth.get_balance(accounts[7].address),
        'contract_dst': web3_right.eth.get_balance(bridge_right.address)
    }


    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])


    # Transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[1].address]), 1, \
            state = state_1)

    # Transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 1, \
            state = state_2)


@pytest.mark.it('AC-016-02: Removing db.')
@pytest.mark.dependency(depends = US_012 + US_013, name = 'AC_016_02', scope = 'session')
def test_AC_016_02(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_016_02.')
    
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])


    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), set([accounts[1].address]), 1)  
    
    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1000.
    assert balance == web3_left.toWei('1000', 'ether'), \
        f'Right bridge has non zero balande: {balanse}.'


    # Exchange.
    exchange_and_check(bridge_right, bridge_left, accounts[5], \
        web3_left.toWei('10', 'ether'), set([accounts[1].address]), 1)   

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1010.
    assert balance == web3_left.toWei('1010', 'ether'), \
        f'Right bridge has bad balande: {balanсe} != {web3_left.toWei("1010", "ether")}.'


    # $ docker-compose down.
    stop_oracle(log, docker, accounts[1].address, remove_db = True)



    # Exchange. No transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[1].address]), 0)

    

    # Exchange. No transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 0)


    state_1 = {
        'block_dst': bridge_left.web3.eth.block_number + 1,
        'balance_dst': web3_left.eth.get_balance(accounts[6].address),
        'contract_dst': web3_left.eth.get_balance(bridge_left.address)
    }

    state_2 = {
        'block_dst': bridge_right.web3.eth.block_number + 1,
        'balance_dst': web3_right.eth.get_balance(accounts[7].address),
        'contract_dst': web3_right.eth.get_balance(bridge_right.address)
    }


    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])


    # Transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[1].address]), 1, \
            state = state_1)

    # Transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 1, \
            state = state_2)


@pytest.mark.it('AC-016-03: Removing db and change validator.')
@pytest.mark.dependency(depends = US_012 + US_013, name = 'AC_016_03', scope = 'session')
def test_AC_016_03(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_016_03.')
    
    default_deployment_environment['VALIDATORS'] = accounts[1].address
    default_deployment_environment['THRESHOLD'] = 1

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    validators_set_left = tmp['left']['validators_set']
    validators_set_right = tmp['right']['validators_set']

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[1])


    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), set([accounts[1].address]), 1)  
    
    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1000.
    assert balance == web3_left.toWei('1000', 'ether'), \
        f'Right bridge has non zero balande: {balanse}.'


    # Exchange.
    exchange_and_check(bridge_right, bridge_left, accounts[5], \
        web3_left.toWei('10', 'ether'), set([accounts[1].address]), 1)   

    balance = web3_right.eth.get_balance(bridge_right.address)

    # Balance 1010.
    assert balance == web3_left.toWei('1010', 'ether'), \
        f'Right bridge has bad balande: {balanсe} != {web3_left.toWei("1010", "ether")}.'


    # $ docker-compose down.
    stop_oracle(log, docker, accounts[1].address, remove_db = True)


    # Exchange. No transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[1].address]), 0)

    

    # Exchange. No transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[1].address]), 0)


    # addValidator
    send_transaction_and_check(web3_left, accounts[0], \
        function = validators_set_left.functions.addValidator(accounts[2].address))

    # addValidator
    send_transaction_and_check(web3_right, accounts[0], \
        function = validators_set_right.functions.addValidator(accounts[2].address))


    # removeValidator
    send_transaction_and_check(web3_left, accounts[0], \
        function = validators_set_left.functions.removeValidator(accounts[1].address))

     # removeValidator
    send_transaction_and_check(web3_right, accounts[0], \
        function = validators_set_right.functions.removeValidator(accounts[1].address))

    state_1 = {
        'block_dst': bridge_left.web3.eth.block_number + 1,
        'balance_dst': web3_left.eth.get_balance(accounts[6].address),
        'contract_dst': web3_left.eth.get_balance(bridge_left.address)
    }

    state_2 = {
        'block_dst': bridge_right.web3.eth.block_number + 1,
        'balance_dst': web3_right.eth.get_balance(accounts[7].address),
        'contract_dst': web3_right.eth.get_balance(bridge_right.address)
    }


    # Oracle with accounts[1].
    start_oracle(log, docker, bridge_left, bridge_right, accounts[2])


    # Transactions.
    exchange_and_check(bridge_right, bridge_left, accounts[6], \
        web3_left.toWei('27', 'ether'), set([accounts[2].address]), 1, \
            state = state_1)

    # Transactions.
    exchange_and_check(bridge_left, bridge_right, accounts[7], \
        web3_left.toWei('15', 'ether'), set([accounts[2].address]), 1, \
            state = state_2)