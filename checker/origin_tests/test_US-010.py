import pytest
from blockchain_tools import send_transaction_and_check, check_events
from helpers import deploy_contracts, random_transaction_id

from . import US_006


@pytest.mark.it('AC-010-01: Send token to bridge right.')
@pytest.mark.dependency(depends=US_006, name='AC_010_01', scope='session')
def test_AC_010_01(docker, log, web3_left, web3_right, accounts, default_deployment_environment):
    log.info('Testing AC_010_01.')
    default_deployment_environment['VALIDATORS'] = accounts[2].address
    default_deployment_environment["THRESHOLD"] = 1
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_right = tmp['right']['bridge']

    # User invoke estimate_gas() for sending 5 native tokens to bridge
    send_transaction_and_check(web3_right, accounts[5],
                               value=web3_left.toWei(5, 'ether'), to=bridge_right.address, revert=True)
    # admin send 200 tokens on right contract
    send_transaction_and_check(web3_right, accounts[0], \
                               function=bridge_right.functions.addLiquidity(), \
                               value=web3_right.toWei('200', 'ether'))
    # check contract balance
    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 200000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    # User invoke estimate_gas() for sending 5 native tokens to bridge
    send_transaction_and_check(web3_right, accounts[5],
                               value=web3_left.toWei(5, 'ether'), to=bridge_right.address, revert=True)

    # Commit movements. transfer from right contract
    balance1 = web3_right.eth.get_balance(accounts[6].address)
    args_for_commit = (accounts[6].address, web3_right.toWei('100', 'ether'), random_transaction_id())
    send_transaction_and_check(web3_right, accounts[2],
                               function=bridge_right.functions.commit(*args_for_commit))
    balance = web3_right.eth.get_balance(accounts[6].address)
    assert balance1 + 100000000000000000000 == balance, \
        f'Wrong balance:\n{accounts[5].address} balance didnt increase.'

    # check contract balance
    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 100000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    # Catching event
    BAI_filter = bridge_right.events.bridgeActionInitiated.createFilter(fromBlock='latest')
    send_transaction_and_check(web3_right, accounts[5],
                               value=web3_left.toWei(5, 'ether'), to=bridge_right.address, revert=False)

    check_events(BAI_filter, {'recipient': accounts[5].address, 'amount': 5000000000000000000})

    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 105000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_left.toWei(10, 'ether'), to=bridge_right.address, revert=False)

    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 115000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    BAI_filter = bridge_right.events.bridgeActionInitiated.createFilter(fromBlock='latest')
    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_left.toWei(15, 'ether'), to=bridge_right.address, revert=False)

    check_events(BAI_filter, {'recipient': accounts[6].address, 'amount': 15000000000000000000})

    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 130000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_left.toWei(75, 'ether'), to=bridge_right.address, revert=True)

    balance1 = web3_right.eth.get_balance(accounts[5].address)
    args_for_commit = (accounts[5].address, web3_right.toWei('50', 'ether'), random_transaction_id())
    send_transaction_and_check(web3_right, accounts[2],
                               function=bridge_right.functions.commit(*args_for_commit))
    balance = web3_right.eth.get_balance(accounts[5].address)
    assert balance1 + web3_right.toWei('50', 'ether') == balance, \
        f'Wrong balance:\n{accounts[5].address} balance didnt increase.'

    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 80000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    BAI_filter = bridge_right.events.bridgeActionInitiated.createFilter(fromBlock='latest')

    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_right.toWei(75, 'ether'), to=bridge_right.address, revert=False)

    check_events(BAI_filter, {'recipient': accounts[6].address, 'amount': web3_right.toWei(75, 'ether')})

    setedLimit = bridge_right.functions.getLiquidityLimit().call()
    assert setedLimit == 155000000000000000000, \
        f'WrongLiquidityLimit:\n{setedLimit}.'

    send_transaction_and_check(web3_right, accounts[6],
                               value=web3_left.toWei(0, 'ether'), to=bridge_right.address, revert=True)
