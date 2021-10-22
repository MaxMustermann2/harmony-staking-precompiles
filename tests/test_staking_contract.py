import pytest
from brownie import StakingContract, MaliciousContract, accounts
from brownie.test.managers.runner import RevertContextManager as reverts
from utils.constants import *
from pyhmy import account
from pyhmy import blockchain
from pyhmy import transaction
from pyhmy import staking
from pyhmy import staking_structures, staking_signing
from pyhmy.numbers import convert_one_to_atto
from brownie.exceptions import VirtualMachineError

@pytest.fixture(scope="module", autouse=True)
def setup():
    accounts.add(pk)
    # deploy contract
    global staking_contract
    StakingContract.deploy({'from': accounts[0]})
    staking_contract = StakingContract[0]

def test_collect_rewards_fail_before_create_validator():
    tx = staking_contract._collectRewards({'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_delegate_fail_before_create_validator():
    tx = staking_contract._delegate(staking_contract.address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_undelegate_fail_before_create_validator():
    tx = staking_contract._undelegate(staking_contract.address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_edit_validator_fail_before_create_validator():
    tx = staking_contract._editValidator(list(newDescription.values()), '0.15', minSelfDelegation, maxTotalDelegation, slotPubKeys[0], slotPubKeys[0], slotKeySigs[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_not_funded():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

    # now move money to the contract to avoid this error, but only enough to fund the initial self delegation
    money_tx = staking_contract.acceptMoney({'value': w3.toWei(Decimal('10000'), 'ether'), 'from': accounts[0].address})
    w3.eth.wait_for_transaction_receipt(money_tx.txid)

def test_create_validator_fail_incorrect_description_length():
    with pytest.raises(ValueError):
        staking_contract._createValidator(list(description.values())[:-1], list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)

def test_create_validator_fail_incorrect_commissionRates_length():
    with pytest.raises(ValueError):
        staking_contract._createValidator(list(description.values()), list(commissionRates.values())[:-1], minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)

def test_create_validator_fail_low_minSelfDelegation():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), amount, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_minSelfDelegation_gt_maxTotalDelegation():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), maxTotalDelegation, minSelfDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_incorrect_bls_length():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeysOfIncorrectLength, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_incorrect_bls_sig_length():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigsOfIncorrectLength, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_bls_sig_mismatch():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigsIncorrect, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_amount_lt_minSelfDelegation():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, amount, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_details_gt_280():
    tx = staking_contract._createValidator(list(description_with_invalid_details.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) == 0)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_success():
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    original_count = len(validators)

    # create the validator
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    assert(len(validators) > original_count)

    # ensure new validator has correct info
    validator_information = staking.get_validator_information(validators[0], endpoint=test_net)
    assert(validator_information['validator']['name'] == description['name'])
    assert(validator_information['validator']['identity'] == description['identity'])

def test_create_validator_fail_already_exists():
    tx = staking_contract._createValidator(list(description.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_with_same_identity():
    # deploy a new contract and make it available for test_create_validator_fail_with_same_bls
    global staking_contract2
    StakingContract.deploy({'from': accounts[0]})
    staking_contract2 = StakingContract[1]

    # give it enough to fund initial self delegation
    money_tx = staking_contract2.acceptMoney({'value': w3.toWei(Decimal('10000'), 'ether'), 'from': accounts[0].address})
    w3.eth.wait_for_transaction_receipt(money_tx.txid)
    # try to set up validator
    tx = staking_contract2._createValidator(list(new_description_with_previous_identity.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_create_validator_fail_with_same_bls():
    tx = staking_contract2._createValidator(list(newDescription.values()), list(commissionRates.values()), minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, minSelfDelegation, {'from': accounts[0].address, 'gas_limit': 5500000, 'gas_price': 1e9})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_edit_validator_fail_incorrect_description_length():
    with pytest.raises(ValueError):
        staking_contract._editValidator(list(newDescription.values())[:-1], '0.15', minSelfDelegation, maxTotalDelegation, slotPubKeys[0], slotPubKeys[0], slotKeySigs[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    validator_information = staking.get_validator_information(validators[0], endpoint=test_net)

    #validator info should remain unchanged
    assert(validator_information['validator']['name'] == description['name'])

def test_edit_validator_fail_rate_gt_max_rate():
    tx = staking_contract._editValidator(list(newDescription.values()), '0.95', minSelfDelegation, maxTotalDelegation, slotPubKeys[0], slotPubKeys[0], slotKeySigs[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_edit_validator_fail_invalid_slot_key_to_remove():
    tx = staking_contract._editValidator(list(newDescription.values()), '0.15', minSelfDelegation, maxTotalDelegation, incorrect_slot_key, slotPubKeys[0], slotKeySigs[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_edit_validator_fail_bls_sig_mismatch():
    tx = staking_contract._editValidator(list(newDescription.values()), '0.15', minSelfDelegation, maxTotalDelegation, slotPubKeys[0], slotPubKeys[0], slotKeySigsIncorrect[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_edit_validator_success():
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    validator_information = staking.get_validator_information(validators[0], endpoint=test_net)
    assert(validator_information['validator']['name'] == description['name'])
    tx = staking_contract._editValidator(list(newDescription.values()), '0.15', minSelfDelegation, maxTotalDelegation, slotPubKeys[0], slotPubKeys[0], slotKeySigs[0], {'from': accounts[0].address, 'gas_limit': 55000000})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    validator_information = staking.get_validator_information(validators[0], endpoint=test_net)
    assert(validator_information['validator']['name'] == newDescription['name'])

def test_delegate_fail_not_funded():
    tx = staking_contract._delegate(staking_contract.address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

    # fund the contract with some money so that delegation can go through
    money_tx = staking_contract.acceptMoney({'value': w3.toWei(Decimal('10000'), 'ether'), 'from': accounts[0].address})
    w3.eth.wait_for_transaction_receipt(money_tx.txid)


def test_delegate_fail_amount_lt_100():
    tx = staking_contract._delegate(staking_contract.address, w3.toWei(Decimal('99'), 'ether'), {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_delegate_fail_invalid_validator():
    tx = staking_contract._delegate(accounts[0].address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_delegate_success():
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    total_delegations_before = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    tx = staking_contract._delegate(staking_contract.address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    total_delegations_after = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    assert(total_delegations_after - total_delegations_before == int(amount))

def test_undelegate_fail_invalid_delegator():
    tx = staking_contract._undelegate(accounts[0].address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_undelegate_fail_amount_gt_delegated():
    tx = staking_contract._undelegate(staking_contract.address, w3.toWei(Decimal('100000'), 'ether'), {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def test_undelegate_success():
    validators = staking.get_all_validator_addresses(endpoint=test_net)
    total_delegations_before = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    tx = staking_contract._undelegate(staking_contract.address, amount, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 1)
    total_delegations_after = int(staking.get_validator_information(validators[0], endpoint=test_net)['total-delegation'])
    assert(total_delegations_before - total_delegations_after == int(amount))

def test_collect_rewards():
    #Should fail since there is no rewards to collect yet
    tx = staking_contract._collectRewards({'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)

def malicious_collect_rewards_fail_to_collect_others_rewards():
    MaliciousContract.deploy({'from': accounts[0]})
    malicious_contract = MaliciousContract[0]
    tx = malicious_contract.collectRewards(staking_contract.address, {'from': accounts[0].address})
    receipt = w3.eth.wait_for_transaction_receipt(tx.txid)
    assert(int(receipt['logs'][0]['data'][-1:]) == 0)
