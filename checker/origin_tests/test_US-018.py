import pytest

from helpers import deploy_contracts, start_oracle, stop_oracle, \
    setLiquidity, exchange_and_check, random_transaction_id

from web3.eth import Account

from eth_account.messages import encode_defunct

from blockchain_tools import send_transaction_and_check, check_events

from . import US_002


def sign_message(account:Account, message:bytes) -> tuple[int, int, int]:    
    signed = account.sign_message(encode_defunct(message))
    
    return signed.r, signed.s, signed.v


@pytest.mark.it('AC-018-01: Token transfer.')
@pytest.mark.dependency(depends = US_002, name = 'AC_018_01', scope = 'session')
def test_AC_018_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_018_01.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # ID.
    tx_hash = random_transaction_id()

    def before_check_callback():
        # Validator.
        send_transaction_and_check(web3_right, accounts[1], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))

        # Validator.
        send_transaction_and_check(web3_right, accounts[2], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))
        

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), \
            set([accounts[1].address, accounts[2].address, accounts[3].address]), 2, \
                before_check_callback = before_check_callback) 
    
    # enableRobustMode()
    send_transaction_and_check(web3_right, accounts[0], \
        function = bridge_right.functions.enableRobustMode())

    # enableRobustMode()
    send_transaction_and_check(web3_left, accounts[0], \
        function = bridge_left.functions.enableRobustMode())


    # ID.
    tx_hash = random_transaction_id()


    # Signature.
    r1, s1, v1 = sign_message(accounts[1], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # Event.
    commits_collected_event = \
        bridge_right.events.commitsCollected.createFilter(fromBlock = 'latest')
    
    # First validator.
    send_transaction_and_check(web3_right, accounts[1], \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))

    # No events.
    check_events(commits_collected_event)



    # Signature.
    r2, s2, v2 = sign_message(accounts[2], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # Second validator.
    send_transaction_and_check(web3_right, accounts[2], \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r2, s2, v2))

    # Event.
    check_events(commits_collected_event, {'id': bytes.fromhex(tx_hash[2:]), 'commits': 2})


    # Signature.
    r3, s3, v3 = sign_message(accounts[3], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # Third validator.
    send_transaction_and_check(web3_right, accounts[3], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r3, s3, v3))

    # getTransferDetails.
    details = bridge_right.functions.getTransferDetails(tx_hash).call()

    assert details[0] == accounts[6].address, \
        f'Details address mismatch: {details[0]} != {accounts[6].address}.'

    assert details[1] == web3_right.toWei('10', 'ether'), \
        f'Details value mismatch: {details[1]} != {web3_right.toWei("10", "ether")}.'


    # getCommit.
    commit = bridge_right.functions.getCommit(tx_hash, 0).call()

    assert [r1, s1, v1] == commit, \
        f'Signature mismatch: {[r1, s1, v1]} != {commit}.'


    # getCommit.
    commit = bridge_right.functions.getCommit(tx_hash, 1).call()

    assert [r2, s2, v2] == commit, \
        f'Signature mismatch: {[r2, s2, v2]} != {commit}.'

    # Balance.
    balance = web3_left.eth.get_balance(accounts[6].address)
    contract = web3_left.eth.get_balance(bridge_left.address)

    # Random address.
    send_transaction_and_check(web3_left, accounts[10], \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1, r2], [s1, s2], [v1, v2]))

    # Updated.
    balance_ = web3_left.eth.get_balance(accounts[6].address)
    contract_ = web3_left.eth.get_balance(bridge_left.address)

    # User.
    assert balance + web3_right.toWei('10', 'ether') == balance_, \
        f'User balance mismatch: {balance + web3_right.toWei("10", "ether")} != {balance_}.'

    # Contract.
    assert contract - web3_right.toWei('10', 'ether') >= contract_, \
        f'User balance mismatch: {contract - web3_right.toWei("10", "ether")} < {contract_}.'



@pytest.mark.it('AC-018-02: Incorrect send to the right address.')
@pytest.mark.dependency(depends = US_002, name = 'AC_018_02', scope = 'session')
def test_AC_018_02(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_018_02.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # ID.
    tx_hash = random_transaction_id()

    def before_check_callback():
        # Validator.
        send_transaction_and_check(web3_right, accounts[1], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))

        # Validator.
        send_transaction_and_check(web3_right, accounts[2], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))
        

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), \
            set([accounts[1].address, accounts[2].address, accounts[3].address]), 2, \
                before_check_callback = before_check_callback) 
    
    # enableRobustMode()
    send_transaction_and_check(web3_right, accounts[0], \
        function = bridge_right.functions.enableRobustMode())


    # ID.
    tx_hash = random_transaction_id()


    # Signature. Validator.
    r1, s1, v1 = sign_message(accounts[1], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # 3. Send validator sign with non-validator account.
    log.info('3. Send validator sign with non-validator account.')
    send_transaction_and_check(web3_right, accounts[10], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))


    # Signature. Not validator
    r1, s1, v1 = sign_message(accounts[10], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # 4. Send not validator sign with validator account.
    log.info('4. Send not validator sign with validator account.')
    send_transaction_and_check(web3_right, accounts[1], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))


    # Signature. Validator.
    r1, s1, v1 = sign_message(accounts[1], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # 5. Send validator sign with validator account but more funds.
    log.info('5. Send validator sign with validator account but more funds.')
    send_transaction_and_check(web3_right, accounts[1], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('20', 'ether'), tx_hash, r1, s1, v1))


    # Signature. Validator.
    r1, s1, v1 = sign_message(accounts[1], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # Event.
    commits_collected_event = \
        bridge_right.events.commitsCollected.createFilter(fromBlock = 'latest')
    

    # 6. First confirm.
    log.info('6. First confirm.')
    send_transaction_and_check(web3_right, accounts[1], \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))

    # No events.
    check_events(commits_collected_event)


    # 7. Cannot confirm again.
    log.info('7. Cannot confirm again.')
    send_transaction_and_check(web3_right, accounts[1], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))


    # Signature. Validator.
    r2, s2, v2 = sign_message(accounts[2], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # 8. Second confirm.
    log.info('8. Second confirm.')
    send_transaction_and_check(web3_right, accounts[2], \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r2, s2, v2))


    # Event.   
    check_events(commits_collected_event, {'id': bytes.fromhex(tx_hash[2:]), 'commits': 2})


    # 9. Cannot confirm again.
    log.info('9. Cannot confirm again.')
    send_transaction_and_check(web3_right, accounts[1], revert = True, \
        function = bridge_right.functions.registerCommit(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash, r1, s1, v1))



@pytest.mark.it('AC-018-03: Incorrect send to the left address.')
@pytest.mark.dependency(depends = US_002, name = 'AC_018_03', scope = 'session')
def test_AC_018_03(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_018_03.')

    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    # Update liquidity.
    setLiquidity(bridge_left, bridge_right, accounts[0], \
        web3_left.toWei('2000', 'ether'))

    # ID.
    tx_hash = random_transaction_id()

    def before_check_callback():
        # Validator.
        send_transaction_and_check(web3_right, accounts[1], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))

        # Validator.
        send_transaction_and_check(web3_right, accounts[2], \
            function = bridge_right.functions.commit(\
                accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))
        

    # Exchange.
    exchange_and_check(bridge_left, bridge_right, accounts[5], \
        web3_left.toWei('1000', 'ether'), \
            set([accounts[1].address, accounts[2].address, accounts[3].address]), 2, \
                before_check_callback = before_check_callback) 
    
    # enableRobustMode()
    send_transaction_and_check(web3_left, accounts[0], \
        function = bridge_left.functions.enableRobustMode())

    # ID.
    tx_hash = random_transaction_id()

    # 3. Commit method disabled.
    log.info('3. Commit method disabled.')
    send_transaction_and_check(web3_left, accounts[1], revert = True, \
        function = bridge_left.functions.commit(\
            accounts[5].address, web3_right.toWei('1000','ether'), tx_hash))



    # Signature. Validator 1.
    r1, s1, v1 = sign_message(accounts[1], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())


    # 4. Random address. Not enought commits.
    log.info('4. Random address. Not enought commits.')
    send_transaction_and_check(web3_left, accounts[10], revert = True, \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1], [s1], [v1]))

    # Signature. Validator 2.
    r2, s2, v2 = sign_message(accounts[2], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    
    # 5. Random address. Differenet value.
    log.info('5. Random address. Differenet value.')
    send_transaction_and_check(web3_left, accounts[10], revert = True, \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('20', 'ether'), \
                tx_hash, [r1, r2], [s1, s2], [v1, v2]))

    
    # 6. Random address. Same commits.
    log.info('6. Random address. Same commits.')
    send_transaction_and_check(web3_left, accounts[10], revert = True, \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1, r1], [s1, s1], [v1, v1]))


    # 7. Random address. Valid.
    log.info('7. Random address. Valid.')
    send_transaction_and_check(web3_left, accounts[10], \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1, r2], [s1, s2], [v1, v2]))

    # 8. Random address. Repeat.
    log.info('8. Random address. Repeat.')
    send_transaction_and_check(web3_left, accounts[9], revert = True, \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1, r2], [s1, s2], [v1, v2]))

    # Signature. Validator 3.
    r3, s3, v3 = sign_message(accounts[3], \
        bridge_right.functions.getRobustModeMessage(\
            accounts[6].address, web3_right.toWei('10', 'ether'), tx_hash).call())

    # 9. Random address. Repeat with different sign.
    log.info('9. Random address. Repeat with different sign.')
    send_transaction_and_check(web3_left, accounts[9], revert = True, \
        function = bridge_left.functions.applyCommits(\
            accounts[6].address, web3_right.toWei('10', 'ether'), \
                tx_hash, [r1, r3], [s1, s3], [v1, v3]))