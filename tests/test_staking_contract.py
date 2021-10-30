import pytest
from brownie import StakingContract, MaliciousContract, accounts
from brownie.test.managers.runner import RevertContextManager as reverts
from utils.constants import *
from pyhmy import account, transaction, staking, signing
from pyhmy.validator import Validator
from pyhmy.numbers import convert_one_to_atto
from brownie.exceptions import VirtualMachineError

def print_gas_consumed(func):
    def inner1(*args, **kwargs):
        # storing time before function execution
        before = account.get_balance(accounts[0].address, endpoint=test_net)
        tx_hash = func(*args, **kwargs)
        after = account.get_balance(accounts[0].address, endpoint=test_net)
        gas = transaction.get_transaction_by_hash(tx_hash, endpoint=test_net)['gasPrice']
        print("Consumed on account {}".format((before-after)/gas))
    return inner1

@pytest.fixture(scope="module", autouse=True)
def setup():
    print("Deploying contract")
    accounts.add(pk)
    # deploy contract
    global staking_contract
    StakingContract.deploy({'from': accounts[0]})
    staking_contract = StakingContract[0]
    print(staking_contract.address)

@pytest.mark.order(1)
@print_gas_consumed
def test_collect_rewards_fail_before_create_validator():
    tx = staking_contract._collectRewards({'from': accounts[0].address, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(2)
@print_gas_consumed
def test_delegate_fail_before_create_validator():
    tx = staking_contract._delegate(accounts[0].address, amount, {'from': accounts[0].address, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(3)
@print_gas_consumed
def test_undelegate_fail_before_create_validator():
    tx = staking_contract._undelegate(accounts[0].address, amount, {'from': accounts[0].address, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

# not really a precompiles test
@pytest.mark.order(4)
def test_create_validator():
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    original_count = len(validators)
    # create the validator (accounts[0].address is already funded)
    validator = Validator(validator_address)
    validator.load(validator_info)
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    # nonce, gas_price, gas_limit, private_key, chain_id
    signed_tx = validator.sign_create_validator_transaction(nonce, int(1e9), 55000000, pk, 2)
    hash = transaction.send_raw_staking_transaction(signed_tx.rawTransaction.hex(), endpoint=test_net)
    # wait for tx to get processed
    while(True):
        tx = transaction.get_staking_transaction_by_hash(hash, endpoint=test_net)
        if tx is not None:
            if tx[ 'blockHash' ] != '0x0000000000000000000000000000000000000000000000000000000000000000':
                break

    # ensure it is created
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) > original_count)

    # ensure it has correct info
    loaded_info = staking.get_validator_information(validators[0], endpoint=test_net)
    assert(loaded_info['validator']['name'] == validator_info['name'])
    assert(loaded_info['validator']['identity'] == validator_info['identity'])

@pytest.mark.order(5)
@print_gas_consumed
def test_delegate_fail_not_funded():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._delegate(accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(6)
# again, not a precompile test
def test_fund_delegate_success():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    # fund the contract with some money so that delegation can go through
    money_tx = staking_contract.acceptMoney({'value': w3.toWei(Decimal('10000'), 'ether'), 'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    w3.eth.wait_for_transaction_receipt(money_tx.txid)

@pytest.mark.order(7)
@print_gas_consumed
def test_delegate_fail_amount_lt_100():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._delegate(accounts[0].address, w3.toWei(Decimal('99'), 'ether'), {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(8)
@print_gas_consumed
def test_delegate_fail_invalid_validator():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._delegate(staking_contract.address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(9)
@print_gas_consumed
def test_delegate_success():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    total_delegations_before = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    tx = staking_contract._delegate(accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    total_delegations_after = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    assert(total_delegations_after - total_delegations_before == int(amount))
    return tx.txid

@pytest.mark.order(10)
@print_gas_consumed
def test_undelegate_fail_invalid_delegator():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._undelegate(staking_contract.address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(11)
@print_gas_consumed
def test_undelegate_fail_amount_gt_delegated():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._undelegate(accounts[0].address, w3.toWei(Decimal('100000'), 'ether'), {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(12)
@print_gas_consumed
def test_undelegate_success():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    total_delegations_before = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    tx = staking_contract._undelegate(accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    total_delegations_after = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    assert(total_delegations_before - total_delegations_after == int(amount))
    return tx.txid

@pytest.mark.order(13)
@print_gas_consumed
def test_collect_rewards_success():
    # should fail since there are no rewards to collect yet
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._collectRewards({'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(14)
# again, not a test for precompiles
def test_deploy_and_fund_malicious_contract():
    global malicious_contract
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    MaliciousContract.deploy({'from': accounts[0], 'nonce': nonce})
    malicious_contract = MaliciousContract[0]
    # make sure victim address is funded
    transaction_dict = {
        'nonce': nonce + 1,
        'gasPrice': int(1e9),
        'gas': 21000,
        'to': victim_address,
        'value': amount,
        'chainId': 2,
        'shardID': 0,
        'toShardID': 0,
    }
    signed_tx = signing.sign_transaction(transaction_dict, private_key=pk)
    _ = transaction.send_and_confirm_raw_transaction(signed_tx.rawTransaction.hex(), endpoint=test_net)

@pytest.mark.order(15)
@print_gas_consumed
def test_delegate_fail_malicious():
    global malicious_contract
    # try to delegate (nonce has to be harcoded below because brownie is slower than pyhmy)
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = malicious_contract.delegate(victim_address, accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid
