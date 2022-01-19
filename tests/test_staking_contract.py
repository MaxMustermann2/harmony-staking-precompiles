import pytest
from dotenv import load_dotenv
from os import getenv
import os.path
import json
import time

from web3 import Web3
from eth_utils import to_checksum_address
from pyhmy import (
    account,
    blockchain,
    contract,
    numbers,
    signing,
    staking,
    transaction,
    staking,
    validator as validator_module,
    util
)
from brownie import (
    accounts,
    Contract,
    StakingContract,
    MaliciousContract,
    MultipleCallsContract,
    ContractWhichReverts,
    TrySubsidizeContract
)

from utils.constants import *


@pytest.fixture( scope = "module", autouse = True )
def setup():
    global w3, endpoint, staking_contract
    print( "Setting up test environment" )
    load_dotenv( ".env" )
    endpoint = getenv( "endpoint" )
    w3 = Web3( Web3.HTTPProvider( endpoint ) )
    accounts.add( pk )
    print( f"Waiting for node at {endpoint} to boot up and reach staking era" )
    current_epoch = 0
    wanted_epoch = 2  # staking epoch
    timeout = 90  # epoch 2 is 14, so +30 seconds for that
    start_time = time.time()
    shard = -1
    while (
        ( shard == 0 or shard == -1 ) and
        ( ( time.time() - start_time ) <= timeout ) and
        ( current_epoch < wanted_epoch )
    ):
        try:
            if shard == -1:
                shard = blockchain.get_shard( endpoint = endpoint )
            current_block_num = blockchain.get_block_number( endpoint )
            if current_block_num > 0:
                # we are producing blocks, so we will reach wanted_epoch soon
                start_time = time.time()
            current_epoch = blockchain.get_current_epoch( endpoint )
            print(
                f"Current block number = {current_block_num}\n" +
                f"Current epoch number = {current_epoch}"
            )
        except KeyboardInterrupt:
            pytext.exit( "KeyboardInterrupt" )
        except:
            pass
        time.sleep( 1 )
    if current_epoch < wanted_epoch:
        pytest.exit( f"Node didn't start in {timeout} seconds, exiting" )
    if shard != 0:
        pytest.exit( f"Shard needs to be 0, got {shard}" )
    print( "Node is booted up" )
    StakingContract.deploy( { 'from': accounts[ 0 ] } )
    staking_contract = StakingContract[ 0 ]
    print( "Main staking contract is at {}".format( staking_contract.address ) )
    print( "Set up test environment" )


@pytest.mark.order( 0 )
def test_epoch():
    epoch = blockchain.get_current_epoch( endpoint )
    epoch_from_contract = staking_contract.epoch()
    print( f"Epoch from pyhmy: {epoch}" )
    print( f"Epoch from contract: {epoch_from_contract}" )
    # might be possible that epoch changes between pyhmy call and contract call
    assert epoch_from_contract >= epoch


@pytest.mark.order( 1 )
def test_collect_rewards_fail_before_create_validator():
    tx = staking_contract._collectRewards(
        {
            'from': accounts[ 0 ].address,
            # 25k for the contract call and another 25k for the staking
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    # no rewards to collect
    # check the last event as a successful tx produces one extra event
    # which goes as the first one
    assert ( int( receipt[ 'logs' ][ -1 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 2 )
def test_delegate_fail_before_create_validator():
    validators = staking.get_all_validator_addresses( endpoint = endpoint )
    if validator_address in validators:
        pytest.skip( 'Validator already exists' )
    tx = staking_contract._delegate(
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 3 )
def test_undelegate_fail_before_create_validator():
    validators = staking.get_all_validator_addresses( endpoint = endpoint )
    if validator_address in validators:
        pytest.skip( 'Validator already exists' )
    tx = staking_contract._undelegate(
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 4 )
def test_delegate_fail_not_funded():
    # create the validator
    create_validator( validator_address, validator_info, pk )
    # now the test
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._delegate(
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 5 )
def test_delegate_fail_amount_lt_100():
    print( "Funding the contract with 100 ONE" )
    fund_contract( 100, staking_contract )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._delegate(
        accounts[ 0 ].address,
        int( numbers.convert_one_to_atto( 99 ) ),
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 6 )
def test_delegate_fail_invalid_validator():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._delegate(
        staking_contract.address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 7 )
def test_delegate_success():
    balance = account.get_balance(
        staking_contract.address,
        endpoint = endpoint
    )
    if balance == 0:
        # useful if called via -k
        fund_contract( 100, staking_contract )
    # same as above
    create_validator( validator_address, validator_info, pk )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    tx = staking_contract._delegate(
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 1 )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert (
        total_delegations_after -
        total_delegations_before == protocol_min_delegation
    )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 8 )
def test_undelegate_fail_invalid_delegator():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._undelegate(
        staking_contract.address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 9 )
def test_undelegate_fail_amount_gt_delegated():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._undelegate(
        accounts[ 0 ].address,
        int( numbers.convert_one_to_atto( 100000 ) ),
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 10 )
def test_collect_rewards_success():
    # check for delegation (useful if running via -k)
    result = staking.get_delegation_by_delegator_and_validator(
        staking_contract.address,
        validator_address,
        endpoint = endpoint
    )
    if not result:
        print( "Delegating because it is missing" )
        test_delegate_success()
    print( "Waiting for rewards to show up" )
    start_block = blockchain.get_block_number( endpoint = endpoint )
    end_block = start_block
    reward = 0
    validator_reward = staking.get_delegation_by_delegator_and_validator(
        validator_address,
        validator_address,
        endpoint = endpoint
    )[ 'reward' ]
    # rewards are distributed every 63/64 blocks, keep double that as a margin
    while ( reward == 0 and end_block - start_block <= 128 ):
        result = staking.get_delegation_by_delegator_and_validator(
            staking_contract.address,
            validator_address,
            endpoint = endpoint
        )
        reward = result[ 'reward' ]
        end_block = blockchain.get_block_number( endpoint = endpoint )
        time.sleep( 2 )
    if reward != 0:
        print( "We have rewards now" )
    else:
        current_validator_reward = staking.get_delegation_by_delegator_and_validator(
            validator_address,
            validator_address,
            endpoint = endpoint
        )[ 'reward' ]
        if current_validator_reward == validator_reward:
            pytest.fail( "The validator is not running" )
        else:
            pytest.fail( "The validator running, unknown reason" )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = staking_contract._collectRewards(
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ -1 ][ 'data' ][ -1 : ] ) == 1 )
    balance = account.get_balance(
        staking_contract.address,
        endpoint = endpoint
    )
    assert balance == reward
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 11 )
def test_undelegate_success():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    tx = staking_contract._undelegate(
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 1 )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert (
        total_delegations_before -
        total_delegations_after == protocol_min_delegation
    )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 12 )
def test_delegate_fail_malicious():
    malicious_contract = deploy_and_fund_malicious_contract()
    # try to delegate
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = malicious_contract.delegate(
        util.convert_one_to_hex( victim_address ),
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    assert ( int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 0 )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 13 )
def test_multiple_calls_success():
    global multiple_calls_contract
    # set up 2 new validators
    make_spare_validators()
    print( "Deploying multiple calls contract" )
    multiple_calls_contract = deploy_multiple_calls_contract()
    print(
        "Multiple calls contract is at {}".format(
            multiple_calls_contract.address
        )
    )
    # fund it with 300 ONE for immediate delegation
    # and another 100 for switchDelegationAndCollectRewards
    # since the undelegated amount will be locked until end of epoch
    print( "Funding multiple calls contract" )
    fund_contract( 400, multiple_calls_contract )
    delegations = []
    for addr in [ accounts[ 0 ].address ] + spare_validators:
        delegations.append(
            {
                'validator': util.convert_one_to_hex( addr ),
                'amount': protocol_min_delegation
            }
        )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    print(
        "Calling delegateMultipleAndCollectRewards with {} delegation(s)"
        .format( len( delegations ) )
    )
    # 5x the gas limit below for 3x delegation + 1x collect rewards + 1x tx
    # 0.5x to spare because a failed transaction causes loss of 25k gas
    tx = multiple_calls_contract.delegateMultipleAndCollectRewards(
        [ list( delegation.values() ) for delegation in delegations ],
        {
            'from': accounts[ 0 ].address,
            'gas_limit': int( once_gas_limit * 5.5 ),
            'nonce': nonce
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    print( f"Gas consumed is {tx.gas_used}" )
    for i in range( len( delegations ) ):
        assert ( int( receipt[ 'logs' ][ i ][ 'data' ][ -1 : ] ) == 1 )
    assert (
        int( receipt[ 'logs' ][ len( delegations ) ][ 'data' ][ -1 : ] ) == 0
    )  # collect rewards (no rewards to collect immediately)
    # now undelegate from second validator, and delegate to first (both equal amounts)
    # note that the balance which is undelegated is not immediately available for redelegation
    # such a redelegation can only be made after close of the epoch
    undelegation = {
        'validator': util.convert_one_to_hex( spare_validators[ 1 ] ),
        'amount': protocol_min_delegation
    }
    delegation = {
        'validator': util.convert_one_to_hex( spare_validators[ 0 ] ),
        'amount': protocol_min_delegation
    }
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    # 4x the gas limit for 3 sub parts + 1x tx
    # 0.5x to spare because a failed transaction causes loss of 25k gas
    print( "Calling switchDelegationAndCollectRewards" )
    tx = multiple_calls_contract.undelegateDelegateAndCollectRewards(
        list( undelegation.values() ),
        list( delegation.values() ),
        {
            'from': accounts[ 0 ].address,
            'gas_limit': int( once_gas_limit * 4.5 ),
            'nonce': nonce
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    print( f"Gas consumed is {tx.gas_used}" )
    assert (
        int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 1
    )  # undelegation
    assert (
        int( receipt[ 'logs' ][ 1 ][ 'data' ][ -1 : ] ) == 1
    )  # delegation
    assert (
        int( receipt[ 'logs' ][ 2 ][ 'data' ][ -1 : ] ) == 0
    )  # collect rewards (no rewards to collect)
    # now undelegate 200 and try to re-delegate 300 (should fail)
    undelegation = {
        'validator': util.convert_one_to_hex( spare_validators[ 0 ] ),
        'amount': protocol_min_delegation * 2
    }
    delegation = {
        'validator': util.convert_one_to_hex( spare_validators[ 1 ] ),
        'amount': protocol_min_delegation * 3
    }
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    print( "Calling switchDelegationAndCollectRewards" )
    # 4x the gas limit for 3 sub parts + 1x tx
    # 0.5x to spare because 2 failed txs causes loss of 25k gas
    tx = multiple_calls_contract.undelegateDelegateAndCollectRewards(
        list( undelegation.values() ),
        list( delegation.values() ),
        {
            'from': accounts[ 0 ].address,
            'gas_limit': int( once_gas_limit * 4.5 ),
            'nonce': nonce
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    print( f"Gas consumed is {tx.gas_used}" )
    assert (
        int( receipt[ 'logs' ][ 0 ][ 'data' ][ -1 : ] ) == 1
    )  # undelegation
    assert (
        int( receipt[ 'logs' ][ 1 ][ 'data' ][ -1 : ] ) == 0
    )  # delegation
    assert (
        int( receipt[ 'logs' ][ 2 ][ 'data' ][ -1 : ] ) == 0
    )  # collect rewards (no rewards to collect)


def deploy_multiple_calls_contract():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    MultipleCallsContract.deploy( {
        'from': accounts[ 0 ],
        'nonce': nonce
    } )
    return MultipleCallsContract[ 0 ]


def fund_contract( how_much, contract ):
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    money_tx = contract.acceptMoney(
        {
            'value': int( numbers.convert_one_to_atto( how_much ) ),
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit
        }
    )
    w3.eth.wait_for_transaction_receipt( money_tx.txid )


def fund_address( how_much, address, **kwargs ):
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    transaction_dict = {
        'nonce': nonce,
        'gasPrice': int( 1e9 ),
        'gas': kwargs.get( 'gas',
                           21000 ),
        'to': address,
        'value': int( numbers.convert_one_to_atto( how_much ) ),
        'chainId': 2,
        'shardID': 0,
        'toShardID': kwargs.get( 'toShardID',
                                 0 ),
    }
    signed_tx = signing.sign_transaction( transaction_dict, private_key = pk )
    return transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )


def create_validator( address, info, private_key ):
    # address must be a bech32 (one...) address
    validators = staking.get_all_validator_addresses( endpoint = endpoint )
    if address in validators:
        return
    balance = account.get_balance( address, endpoint = endpoint )
    if balance < numbers.convert_one_to_atto( 10050 ):
        # 10k self delegation + some for gas
        fund_address( 10050, util.convert_one_to_hex( address ) )
    print( "Creating the validator at {} using pyhmy".format( address ) )
    validators = staking.get_all_validator_addresses( endpoint = endpoint )
    original_count = len( validators )
    validator = validator_module.Validator( address )
    validator.load( info )
    nonce = account.get_account_nonce( address, 'latest', endpoint = endpoint )
    # nonce, gas_price, gas_limit, private_key, chain_id
    signed_tx = validator.sign_create_validator_transaction(
        nonce,
        int( 1e9 ),
        55000000,   # gas limit
        private_key,
        2           # chain id
    )
    hash = transaction.send_raw_staking_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )
    # wait for tx to get processed
    while ( True ):
        tx = transaction.get_staking_transaction_by_hash(
            hash,
            endpoint = endpoint
        )
        if tx is not None:
            block_hash = tx.get( "blockHash", "0x00" )
            unique_chars = "".join( set( list( block_hash[ 2 : ] ) ) )
            if unique_chars != "0":  # meaning non 0 block hash
                break  # out of the while loop
        time.sleep( 0.5 )
    # ensure it is created
    validators = staking.get_all_validator_addresses( endpoint = endpoint )
    assert ( len( validators ) > original_count )
    # ensure it has correct info
    loaded_info = staking.get_validator_information(
        address,
        endpoint = endpoint
    )
    assert ( loaded_info[ 'validator' ][ 'name' ] == info[ 'name' ] )
    assert ( loaded_info[ 'validator' ][ 'identity' ] == info[ 'identity' ] )


def make_spare_validators():
    print( "Making spare validators" )
    for addr, info, private_key in zip( spare_validators, spare_validator_infos,
                                       spare_validator_pks ):
        create_validator( addr, info, private_key )


def deploy_and_fund_malicious_contract():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    MaliciousContract.deploy( {
        'from': accounts[ 0 ],
        'nonce': nonce
    } )
    malicious_contract = MaliciousContract[ 0 ]
    # make sure victim address and contract address both are funded
    # this way we are sure that the delegation failure is the malice and not low balance
    # of course we can see the logs for this but still
    fund_address( 100, victim_address )
    fund_address( 100, malicious_contract.address )
    return malicious_contract


@pytest.mark.order( 13 )
def test_many_calls_success():
    global multiple_calls_contract
    multiple_calls_contract = deploy_multiple_calls_contract()
    # chosen based on testing to get no ErrOutOfGas
    # go any higher and the node will complain
    how_many = 3094
    print(
        "Attempting {} precompile calls to check block time".format( how_many )
    )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    tx = multiple_calls_contract.multipleCollectRewards(
        how_many,
        {
            'from': accounts[ 0 ].address,
            'gas_limit': block_gas_limit,
            'nonce': nonce
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    block_number = receipt[ 'blockNumber' ]
    timestamp1 = blockchain.get_block_by_number(
        block_number,
        endpoint = endpoint
    )[ 'timestamp' ]
    timestamp2 = blockchain.get_block_by_number(
        block_number - 1,
        endpoint = endpoint
    )[ 'timestamp' ]
    diff = int( timestamp1 - timestamp2 )
    print( "Block #{} was produced in {} seconds".format( block_number, diff ) )
    assert diff == 2
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 14 )
def test_contract_which_reverts_success():
    print( "Deploying contract which reverts" )
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    ContractWhichReverts.deploy( {
        'from': accounts[ 0 ],
        'nonce': nonce
    } )
    contract_which_reverts = ContractWhichReverts[ 0 ]
    print( "Deployed contract which reverts" )

    print( "Funding the contract, which reverts, with 100 ONE" )
    fund_contract( 100, contract_which_reverts )

    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    print( "Attempting a delegate and revert" )
    with pytest.raises( ValueError ) as exception:
        tx = contract_which_reverts.delegateAndRevert(
            accounts[ 0 ].address,
            protocol_min_delegation,
            {
                'from': accounts[ 0 ].address,
                'nonce': nonce,
                'gas_limit': once_gas_limit * 2,
            }
        )
    assert "Execution reverted" in str( exception.value )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert ( total_delegations_after - total_delegations_before == 0 )
    print( "Delegations are unchanged" )


@pytest.mark.order( 15 )
def test_eoa_access_success():
    with open(
        os.path.join(
            os.path.split( __file__ )[ 0 ],
            '../build/contracts/StakingPrecompilesSelectors.json'
        )
    ) as f:
        abi = json.load( f )[ "abi" ]
    # on Vanilla brownie, this will raise a ContractNotFound because of missing bytecode
    # but just the ABI is enough to interact with the contract
    # https://github.com/MaxMustermann2/brownie/commit/8ae2995159c06eddd7e2098a984e08d27542b79f
    precompile = Contract.from_abi(
        "StakingPrecompile",    # any name works
        "0x00000000000000000000000000000000000000FC",
        abi
    )
    nonce = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    tx = precompile.Delegate(
        accounts[ 0 ].address,
        accounts[ 0 ].address,
        protocol_min_delegation,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 2,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert (
        total_delegations_after -
        total_delegations_before == protocol_min_delegation
    )
    print( f"Gas consumed is {tx.gas_used}" )


@pytest.mark.order( 16 )
def test_eoa_subsidize_success():
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = endpoint
    )
    TrySubsidizeContract.deploy( {
        'from': accounts[ 0 ],
        'nonce': nonce
    } )
    try_subsidized_contract = TrySubsidizeContract[ 0 ]
    total_delegations_before = int(
        staking.get_validator_information(
            accounts[ 0 ].address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    nonce = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    delegations = [
        {
            'validator': util.convert_one_to_hex( accounts[ 0 ].address ),
            'amount': protocol_min_delegation,
        }
    ] * 5
    tx = try_subsidized_contract.delegateDelegate(
        [ list( delegation.values() ) for delegation in delegations ],
        {
            'from': accounts[ 0 ].address,
            'gas_limit': int( once_gas_limit * ( 1.5 + len( delegations ) ) ),
            'nonce': nonce
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    total_delegations_after = int(
        staking.get_validator_information(
            accounts[ 0 ].address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert (
        total_delegations_after -
        total_delegations_before == protocol_min_delegation *
        len( delegations )
    )
    print( f"Gas consumed is {tx.gas_used}" )
    assert tx.gas_used >= once_gas_limit * len( delegations )
    print( f"This is >= than {len(delegations) * once_gas_limit}" )


@pytest.mark.order( 17 )
def test_shard_1_fail():
    endpoint_shard1 = os.getenv( 'endpoint_shard1' )
    assert blockchain.get_shard( endpoint_shard1 ) == 1
    if blockchain.get_current_epoch( endpoint ) < 2:
        pytest.skip( "Skipped cross shard test as epoch < 2" )
    # brownie would need a new network and new balance on shard 1
    # so just deploy manually
    print( "Deploying contract on shard 1" )
    contract_tx = {
        'chainId': 2,
        'data': StakingContract.bytecode,
        'from': accounts[ 0 ].address,
        'gas': once_gas_limit * 15,  # contract creation
        'gasPrice': int( 1e9 ),
        'nonce': account.get_account_nonce(
            accounts[ 0 ].address,
            'latest',
            endpoint = endpoint
        ),
        'shardID': 0,
        'toShardID': 1
    }
    signed_tx = signing.sign_transaction( contract_tx, pk )
    ctx_hash = transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )[ 'hash' ]
    contract_address = transaction.get_transaction_receipt(
        ctx_hash,
        endpoint
    )[ 'contractAddress' ]
    deployed_code = contract.get_code(
        util.convert_one_to_hex( contract_address ),
        'latest',
        endpoint = endpoint
    )
    assert len( deployed_code ) > 2, "Could not deploy contract"
    print( f"Contract deployed at {contract_address} on shard 1" )
    staking_contract_w3 = w3.eth.contract(
        abi = StakingContract.abi,
        address = to_checksum_address( contract_address )
    )
    print( "Funding contract on shard 1" )
    # fund from shard 0 to shard 1, so endpoint stays the same
    tx_dict_funding = staking_contract_w3.functions.acceptMoney(
    ).buildTransaction(
        {
            'nonce': account.get_account_nonce(
                accounts[ 0 ].address,
                'latest',
                endpoint = endpoint
            ),
            'gasPrice': int( 1e9 ),
            'gas': once_gas_limit * 2,
            'chainId': 2,
            'shardID': 0,
            'toShardID': 1,
            'value': protocol_min_delegation,
        }
    )
    signed_tx = signing.sign_transaction( tx_dict_funding, pk )
    print( "Confirming contract funding from shard 0" )
    cx_hash = transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )[ 'hash' ]
    print( "Confirming contract funding to shard 1" )
    cx_receipt = None
    while cx_receipt is None:
        cx_receipt = transaction.get_cx_receipt_by_hash(
            cx_hash,
            endpoint_shard1
        )
    balance = account.get_balance(
        contract_address,
        endpoint = endpoint_shard1
    )
    assert balance == protocol_min_delegation
    print( "Delegating for contract on shard 1" )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint  # call on beacon shard
        )[ 'total-delegation' ]
    )
    tx_dict = staking_contract_w3.functions._delegate(
        accounts[ 0 ].address,
        protocol_min_delegation
    ).buildTransaction(
        {
            'nonce': account.get_account_nonce(
                accounts[ 0 ].address,
                'latest',
                endpoint = endpoint_shard1
            ),
            'gasPrice': int( 1e9 ),
            'gas': once_gas_limit * 2,
            'chainId': 2,
            'shardID': 1,
            'toShardID': 1,
            'value': 0,
        }
    )
    signed_tx = signing.sign_transaction( tx_dict, pk )
    tx_hash = transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint_shard1
    )[ 'hash' ]
    balance = account.get_balance(
        contract_address,
        endpoint = endpoint_shard1
    )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert total_delegations_after == total_delegations_before
    assert balance == protocol_min_delegation
    print( "As expected, delegation on shard 1 did not go through" )

    print( "Delegating for contract on shard 0" )
    tx_dict_funding[ 'toShardID' ] = 0
    tx_dict_funding[ 'nonce' ] = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    signed_tx = signing.sign_transaction( tx_dict_funding, pk )
    print( "Confirming contract funding on shard 0" )
    tx_hash = transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )[ 'hash' ]
    tx_dict[ 'shardID' ] = 0
    tx_dict[ 'nonce' ] = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    signed_tx = signing.sign_transaction( tx_dict, pk )
    total_delegations_before = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    tx_hash = transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = endpoint
    )[ 'hash' ]
    balance = account.get_balance( contract_address, endpoint = endpoint )
    total_delegations_after = int(
        staking.get_validator_information(
            validator_address,
            endpoint = endpoint
        )[ 'total-delegation' ]
    )
    assert balance == 0
    assert (
        total_delegations_after -
        total_delegations_before == protocol_min_delegation
    )
    print( "Delegation on shard 0 went through" )


@pytest.mark.order( 18 )
def test_eoa_migrate():
    # useful if used via -k
    create_validator( validator_address, validator_info, pk )
    with open(
        os.path.join(
            os.path.split( __file__ )[ 0 ],
            '../build/contracts/StakingPrecompilesSelectors.json'
        )
    ) as f:
        abi = json.load( f )[ "abi" ]
    # on Vanilla brownie, this will raise a ContractNotFound because of missing bytecode
    # but just the ABI is enough to interact with the contract
    # https://github.com/MaxMustermann2/brownie/commit/8ae2995159c06eddd7e2098a984e08d27542b79f
    precompile = Contract.from_abi(
        "StakingMigrationPrecompile",    # any name works
        "0x00000000000000000000000000000000000000FC",
        abi
    )
    nonce = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    self_delegation_before = (
        staking.get_delegation_by_delegator_and_validator(
            validator_address,
            validator_address,
            endpoint = endpoint
        ) or {}
    ).get( 'amount',
           0 )
    # test_eoa_access_success and test_eoa_subsidize_success
    # increase the self_delegation_before by 600 ONE
    if self_delegation_before < protocol_min_delegation * 100:
        pytest.skip( 'Already migrated' )
    contract_delegation_before = (
        staking.get_delegation_by_delegator_and_validator(
            staking_contract.address,
            validator_address,
            endpoint = endpoint
        ) or {}
    ).get( 'amount',
           0 )
    # we get booted off due to low uptime, so this check is useless
    # validator_status_before = staking.get_validator_information(
    #     validator_address,
    #     endpoint = endpoint
    # )[ 'active-status' ]
    # assert validator_status_before == 'active'
    tx = precompile.Migrate(
        accounts[ 0 ].address,
        staking_contract.address,
        {
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit * 50,
        }
    )
    receipt = w3.eth.wait_for_transaction_receipt( tx.txid )
    self_delegation_after = (
        staking.get_delegation_by_delegator_and_validator(
            validator_address,
            validator_address,
            endpoint = endpoint
        ) or {}
    ).get( 'amount',
           0 )
    contract_delegation_after = (
        staking.get_delegation_by_delegator_and_validator(
            staking_contract.address,
            validator_address,
            endpoint = endpoint
        ) or {}
    ).get( 'amount',
           0 )
    validator_status_after = staking.get_validator_information(
        validator_address,
        endpoint = endpoint
    )[ 'active-status' ]
    assert (
        contract_delegation_after -
        self_delegation_after == self_delegation_before -
        contract_delegation_before
    )
    # assert validator_status_before != validator_status_after
    assert validator_status_after == 'inactive'
    print( f"Gas consumed is {tx.gas_used}" )
