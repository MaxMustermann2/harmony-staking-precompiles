import pytest
from brownie import StakingContract, MaliciousContract, MultipleCallsContract, ContractWhichReverts, accounts
from utils.constants import *
from pyhmy import account, transaction, staking, signing, blockchain
from pyhmy.validator import Validator

def print_gas_consumed(func):
    def inner1(*args, **kwargs):
        before = account.get_balance(accounts[0].address, endpoint=test_net)
        tx_hash = func(*args, **kwargs)
        if isinstance(tx_hash, tuple):
            before, tx_hash = tx_hash
        after = account.get_balance(accounts[0].address, endpoint=test_net)
        gas = transaction.get_transaction_by_hash(tx_hash, endpoint=test_net)['gasPrice']
        print("Gas consumed is {}".format((before-after)/gas))
    return inner1

@pytest.fixture(scope="module", autouse=True)
def setup():
    print("Setting up test environment")
    accounts.add(pk)
    # deploy contract
    global staking_contract
    StakingContract.deploy({'from': accounts[0]})
    staking_contract = StakingContract[0]
    print("Main staking contract is at {}".format(staking_contract.address))
    print("Set up test environment")

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

@pytest.mark.order(4)
@print_gas_consumed
def test_delegate_fail_not_funded():
    # create the validator
    print("Creating the validator at {} using the Harmony SDK".format(validator_address))
    create_validator(validator_address, validator_info, pk)
    # now the test
    before = account.get_balance(accounts[0].address, endpoint=test_net)
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._delegate(accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return before, tx.txid

@pytest.mark.order(5)
@print_gas_consumed
def test_delegate_fail_amount_lt_100():
    print("Funding the contract with 100 ONE")
    fund_contract(100, staking_contract)
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    before = account.get_balance(accounts[0].address, endpoint=test_net)
    tx = staking_contract._delegate(accounts[0].address, w3.toWei(Decimal('99'), 'ether'), {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return before, tx.txid

@pytest.mark.order(6)
@print_gas_consumed
def test_delegate_fail_invalid_validator():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._delegate(staking_contract.address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(7)
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

@pytest.mark.order(8)
@print_gas_consumed
def test_undelegate_fail_invalid_delegator():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._undelegate(staking_contract.address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(9)
@print_gas_consumed
def test_undelegate_fail_amount_gt_delegated():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._undelegate(accounts[0].address, w3.toWei(Decimal('100000'), 'ether'), {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return tx.txid

@pytest.mark.order(10)
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

@pytest.mark.order(11)
@print_gas_consumed
def test_collect_rewards_success():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = staking_contract._collectRewards({'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)   # should fail since there are no rewards to collect yet
    return tx.txid

@pytest.mark.order(12)
@print_gas_consumed
def test_delegate_fail_malicious():
    malicious_contract = deploy_and_fund_malicious_contract()
    # try to delegate
    before = account.get_balance(accounts[0].address, endpoint=test_net)
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = malicious_contract.delegate(victim_address, accounts[0].address, amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
    return before, tx.txid

@pytest.mark.order(13)
def test_multiple_calls_success():
    global multiple_calls_contract
    # set up 2 new validators
    make_spare_validators()
    print("Deploying multiple calls contract")
    multiple_calls_contract = deploy_multiple_calls_contract()
    print("Multiple calls contract is at {}".format(multiple_calls_contract.address))
    # fund it with 300 ONE
    print("Funding multiple calls contract")
    fund_contract(400, multiple_calls_contract)
    delegations = []
    for addr in [accounts[0].address] + spare_validators:
        delegations.append({
            'validator': convert_one_to_hex(addr),
            'amount': amount
        })
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    print("Calling delegateMultipleAndCollectRewards with {} delegation(s)".format(len(delegations)))
    # 4x the gas limit below for 3x delegation + 1x collect rewards
    tx = multiple_calls_contract.delegateMultipleAndCollectRewards([list(delegation.values()) for delegation in delegations],
        {'from': accounts[0].address, 'gas_limit': gas_limit * 4, 'nonce': nonce})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)   # first delegation
    assert(int(receipt['logs'][1]['data'][-1:]) == 1)   # second delegation
    assert(int(receipt['logs'][2]['data'][-1:]) == 1)   # third delegation
    assert(int(receipt['logs'][3]['data'][-1:]) == 0)   # collect rewards (no rewards to collect)
    # now undelegate from second validator, and delegate to first (both equal amounts)
    # note that the balance which is undelegated is not immediately available for redelegation
    # such a redelegation can only be made after close of the epoch
    undelegation = {'validator': convert_one_to_hex(spare_validators[1]), 'amount': amount}
    delegation = {'validator': convert_one_to_hex(spare_validators[0]), 'amount': amount}
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    # 3x the gas limit for 3 sub parts
    print("Calling switchDelegationAndCollectRewards")
    tx = multiple_calls_contract.undelegateDelegateAndCollectRewards(list(undelegation.values()), list(delegation.values()),
        {'from': accounts[0].address, 'gas_limit': gas_limit * 3, 'nonce': nonce})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)   # undelegation
    assert(int(receipt['logs'][1]['data'][-1:]) == 1)   # delegation
    assert(int(receipt['logs'][2]['data'][-1:]) == 0)   # collect rewards (no rewards to collect)
    # now undelegate 200 and try to re-delegate 300 (should fail)
    undelegation = {'validator': convert_one_to_hex(spare_validators[0]), 'amount': amount * 2}
    delegation = {'validator': convert_one_to_hex(spare_validators[1]), 'amount': amount * 3}
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    print("Calling switchDelegationAndCollectRewards")
    tx = multiple_calls_contract.undelegateDelegateAndCollectRewards(list(undelegation.values()), list(delegation.values()),
        {'from': accounts[0].address, 'gas_limit': gas_limit * 3, 'nonce': nonce})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)   # undelegation
    assert(int(receipt['logs'][1]['data'][-1:]) == 0)   # delegation
    assert(int(receipt['logs'][2]['data'][-1:]) == 0)   # collect rewards (no rewards to collect)

def deploy_multiple_calls_contract():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    MultipleCallsContract.deploy({'from': accounts[0], 'nonce': nonce})
    return MultipleCallsContract[0]

def fund_contract(how_much, contract):
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    money_tx = contract.acceptMoney({'value': w3.toWei(Decimal(how_much), 'ether'),
        'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    w3.eth.wait_for_transaction_receipt(money_tx.txid)

def fund_address(how_much, address):
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    transaction_dict = {
        'nonce': nonce,
        'gasPrice': int(1e9),
        'gas': 21000,
        'to': address,
        'value': w3.toWei(Decimal(how_much), 'ether'),
        'chainId': 2,
        'shardID': 0,
        'toShardID': 0,
    }
    signed_tx = signing.sign_transaction(transaction_dict, private_key=pk)
    _ = transaction.send_and_confirm_raw_transaction(signed_tx.rawTransaction.hex(), endpoint=test_net)

def create_validator(address, info, private_key):
    # address must be a bech32 (one...) address
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    original_count = len(validators)
    validator = Validator(address)
    validator.load(info)
    nonce = account.get_account_nonce(address, 'latest', endpoint=test_net)
    # nonce, gas_price, gas_limit, private_key, chain_id
    signed_tx = validator.sign_create_validator_transaction(nonce, int(1e9), 55000000, private_key, 2)
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
    loaded_info = staking.get_validator_information(address, endpoint=test_net)
    assert(loaded_info['validator']['name'] == info['name'])
    assert(loaded_info['validator']['identity'] == info['identity'])

def make_spare_validators():
    print("Making spare validators")
    for addr in spare_validators:
        print("Funding validator {}".format(addr))
        # 10k self delegation + some for gas
        fund_address(10050, convert_one_to_hex(addr))
    for addr, info, private_key in zip(spare_validators, spare_validator_infos, spare_validator_pks):
        print("Creating validator {}".format(addr))
        create_validator(addr, info, private_key)

def deploy_and_fund_malicious_contract():
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    MaliciousContract.deploy({'from': accounts[0], 'nonce': nonce})
    malicious_contract = MaliciousContract[0]
    # make sure victim address is funded
    # this way we are sure that the delegation failure is the malice and not low balance
    # of course we can see the logs for this but still
    fund_address(100, victim_address)
    return malicious_contract

@pytest.mark.order(13)
def test_many_calls_success():
    global multiple_calls_contract
    multiple_calls_contract = deploy_multiple_calls_contract()
    how_many = int(80000000 / 25000) # block gas limit / tx gas limit
    print("Attempting {} precompile calls to check block time".format(how_many))
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    tx = multiple_calls_contract.multipleCollectRewards(how_many,
        {'from': accounts[0].address, 'gas_limit': gas_limit * how_many, 'nonce': nonce})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    block_number = receipt['blockNumber']
    timestamp1 = blockchain.get_block_by_number(block_number, endpoint=test_net)['timestamp']
    timestamp2 = blockchain.get_block_by_number(block_number-1, endpoint=test_net)['timestamp']
    print("Block #{} was produced in {} seconds".format(block_number, timestamp1 - timestamp2))

@pytest.mark.order(14)
def test_contract_which_reverts():
    print("Deploying contract which reverts")
    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    ContractWhichReverts.deploy({'from': accounts[0], 'nonce': nonce})
    contract_which_reverts = ContractWhichReverts[0]
    print("Deployed contract which reverts")

    print("Funding the contract, which reverts, with 100 ONE")
    fund_contract(100, contract_which_reverts)

    nonce = account.get_account_nonce(validator_address, 'latest', endpoint=test_net)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    total_delegations_before = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    print("Attempting a delegate and revert")
    with pytest.raises(ValueError) as exception:
        tx = contract_which_reverts.delegateAndRevert(accounts[0].address,
            amount, {'from': accounts[0].address, 'nonce': nonce, 'gas_limit': gas_limit})
    assert "Execution reverted" in str(exception.value)
    total_delegations_after = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    assert(total_delegations_after - total_delegations_before == 0)
    print("Delegations are unchanged")
