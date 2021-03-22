import pytest

from helpers import deploy_contracts, start_oracle
from blockchain_tools import send_transaction_and_check, check_events


@pytest.mark.it('AC-012-01: Send event to the right.')
@pytest.mark.dependency(depends = [], name = 'AC_012_01', scope = 'session')
def test_AC_012_01(docker, log, web3_left, web3_right, accounts, \
    default_deployment_environment):

    log.info('Testing AC_012_01.')
    
    tmp = deploy_contracts(docker, log, web3_left, web3_right, default_deployment_environment)

    bridge_left = tmp['left']['bridge']
    bridge_right = tmp['right']['bridge']  
    
    start_oracle(log, web3_left, web3_right, bridge_left, bridge_right, accounts[10])
    