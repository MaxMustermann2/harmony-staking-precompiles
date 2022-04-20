from brownie import ( accounts, Contract, ReadOnlyStakingPrecompile )
from dotenv import load_dotenv
import json
from os import getenv
import os.path
from pyhmy import (
    account,
    blockchain,
    numbers,
    signing,
    staking,
    staking_signing,
    transaction,
    util,
    validator as validator_module
)
import pytest
import time
from utils.constants import *
from web3 import Web3


@pytest.fixture( scope = "module", autouse = True )
def setup():
    global web3, deployed_contract, read_only_precompile, endpoint
    print( "Setting up test environment" )
    load_dotenv( ".env" )
    endpoint = getenv( "endpoint" )
    timeout = 90
    current_epoch = 0
    wanted_epoch = 2
    start_time = time.time()
    web3 = Web3( Web3.HTTPProvider( endpoint ) )
    shard = -1
    print( f"Waiting for node at {endpoint} to boot up and reach staking era" )
    while (
        ( shard == 0 or shard == -1 ) and
        ( ( time.time() - start_time ) <= timeout ) and
        ( current_epoch < wanted_epoch )
    ):
        try:
            current_block_num = blockchain.get_block_number( endpoint )
            if current_block_num > 0:
                # we are producing blocks, so we will reach wanted_epoch soon
                start_time = time.time()
            current_epoch = blockchain.get_current_epoch( endpoint )
            print(
                f"Current block number = {current_block_num}\n" +
                f"Current epoch number = {current_epoch}"
            )
            if shard == -1:
                shard = blockchain.get_shard( endpoint = endpoint )
        except KeyboardInterrupt:
            pytext.exit( "KeyboardInterrupt" )
        except:
            pass
        time.sleep( 1 )
    if shard != 0:
        pytest.exit( f"Shard needs to be 0, got {shard}" )
    if current_epoch < wanted_epoch:
        pytest.exit( f"Node didn't start in {timeout} seconds, exiting" )
    print( "Node is booted up" )
    accounts.add( pk )
    nonce = account.get_account_nonce(
        accounts[ 0 ].address,
        'latest',
        endpoint = endpoint
    )
    ReadOnlyStakingPrecompile.deploy(
        {
            'from': accounts[ 0 ],
            'nonce': nonce
        }
    )
    deployed_contract = ReadOnlyStakingPrecompile[ -1 ]
    read_only_precompile = Contract.from_abi(
        "ReadOnlyStakingPrecompile",
        "0x00000000000000000000000000000000000000FA",
        ReadOnlyStakingPrecompile.abi,
    )
    # make the validator
    create_validator( validator_address, validator_info, pk )
    # fund these two guys
    print( "Funding spare addresses" )
    for i in range( 2 ):
        accounts.add()
        if accounts[ i + 1 ].balance() < web3.toWei( 500, 'ether' ):
            nonce = account.get_account_nonce(
                accounts[ 0 ].address,
                'latest',
                endpoint = endpoint
            )
            accounts[ 0 ].transfer(
                accounts[ i + 1 ],
                web3.toWei( 500,
                            'ether' ),
                nonce = nonce
            )
    # have them delegate and then undelegate
    with open(
        os.path.join(
            os.path.split( __file__ )[ 0 ],
            '../build/contracts/StakingPrecompilesSelectors.json'
        )
    ) as f:
        abi = json.load( f )[ "abi" ]
    precompile = Contract.from_abi(
        "StakingPrecompile",
        "0x00000000000000000000000000000000000000FC",
        abi
    )
    print( "Delegating from spare addresses" )
    nonce = account.get_account_nonce(
        accounts[ 1 ].address,
        'latest',
        endpoint = endpoint
    )
    tx = precompile.Delegate(
        accounts[ 1 ].address,
        accounts[ 0 ].address,
        web3.toWei( 400,
                    'ether' ),
        {
            'from': accounts[ 1 ].address,
            'nonce': nonce,
        }
    )
    nonce = account.get_account_nonce(
        accounts[ 2 ].address,
        'latest',
        endpoint = endpoint
    )
    tx = precompile.Delegate(
        accounts[ 2 ].address,
        accounts[ 0 ].address,
        web3.toWei( 300,
                    'ether' ),
        {
            'from': accounts[ 2 ].address,
            'nonce': nonce,
        }
    )
    print( "Waiting for one epoch to close" )
    while ( web3.eth.block_number < tx.block_number + 10 ):
        time.sleep( 1 )
    print( "Undelegating from spare addresses" )
    nonce = account.get_account_nonce(
        accounts[ 1 ].address,
        'latest',
        endpoint = endpoint
    )
    tx = precompile.Undelegate(
        accounts[ 1 ].address,
        accounts[ 0 ].address,
        web3.toWei( 100,
                    'ether' ),
        {
            'from': accounts[ 1 ].address,
            'nonce': nonce,
        }
    )
    nonce = account.get_account_nonce(
        accounts[ 2 ].address,
        'latest',
        endpoint = endpoint
    )
    tx = precompile.Undelegate(
        accounts[ 2 ].address,
        accounts[ 0 ].address,
        web3.toWei( 200,
                    'ether' ),
        {
            'from': accounts[ 2 ].address,
            'nonce': nonce,
        }
    )
    print( "Waiting for one epoch to close" )
    while ( web3.eth.block_number < tx.block_number + 10 ):
        time.sleep( 1 )


# test this first to avoid case when no redelegation balance
def test_getBalanceAvailableForRedelegation():
    expected_values = [ web3.toWei( 100, 'ether' ), web3.toWei( 200, 'ether' ) ]
    for delegator, expected_value in zip( accounts[ 1 : ], expected_values ):
        deployed_value = deployed_contract.getBalanceAvailableForRedelegation(
            delegator.address,
        )
        precompile_value = read_only_precompile.getBalanceAvailableForRedelegation(
            delegator.address,
        )
        sdk_value = staking.get_available_redelegation_balance(
            delegator.address,
            endpoint
        )
        assert deployed_value == precompile_value == sdk_value == expected_value, \
            f"Deployedee: {deployed_value}\n" \
            f"Precompile: {precompile_value}\n" \
            f"SDK  Value: {sdk_value}\n" \
            f"Expe Value: {expected_value}"


def test_getDelegationByDelegatorAndValidator():
    expected_values = [ web3.toWei( 300, 'ether' ), web3.toWei( 100, 'ether' ) ]
    for delegator, expected_value in zip( accounts[ 1 : ], expected_values ):
        deployed_value = deployed_contract.getDelegationByDelegatorAndValidator(
            delegator.address,
            accounts[ 0 ].address
        )
        precompile_value = read_only_precompile.getDelegationByDelegatorAndValidator(
            delegator.address,
            accounts[ 0 ].address
        )
        sdk_value = staking.get_delegation_by_delegator_and_validator(
            delegator.address,
            accounts[ 0 ].address,
            endpoint
        )[ 'amount' ]
        assert deployed_value == precompile_value == sdk_value == expected_value, \
            f"Deployedee: {deployed_value}\n" \
            f"Precompile: {precompile_value}\n" \
            f"SDK  Value: {sdk_value}\n" \
            f"Expe Value: {expected_value}"


def test_getValidatorTotalDelegation():
    deployed_value = deployed_contract.getValidatorTotalDelegation(
        accounts[ 0 ]
    )
    precompile_value = read_only_precompile.getValidatorTotalDelegation(
        accounts[ 0 ]
    )
    sdk_value = sum(
        [
            x[ 'amount' ] for x in staking
            .get_delegations_by_validator( accounts[ 0 ].address,
                                           endpoint )
        ]
    )
    assert deployed_value == precompile_value == sdk_value, \
            f"Deployedee: {deployed_value}\n" \
            f"Precompile: {precompile_value}\n" \
            f"SDK  Value: {sdk_value}\n"


def test_getValidatorTotalDelegationFail():
    if len( accounts ) < 3:
        accounts.add( pk )
        for i, spare_pk in enumerate( spare_pks ):
            accounts.add( spare_pk )
    with pytest.raises( ValueError ) as exception:
        deployed_value = deployed_contract.getValidatorTotalDelegation(
            accounts[ 1 ]
        )
    assert "the call likely reverted" in str( exception.value )
    with pytest.raises( ValueError ) as exception:
        precompile_value = read_only_precompile.getValidatorTotalDelegation(
            accounts[ 1 ]
        )
    assert "the call likely reverted" in str( exception.value )


def test_getValidatorMaxTotalDelegation():
    deployed_value = deployed_contract.getValidatorMaxTotalDelegation(
        accounts[ 0 ]
    )
    precompile_value = read_only_precompile.getValidatorMaxTotalDelegation(
        accounts[ 0 ]
    )
    sdk_value = staking.get_validator_information(
        accounts[ 0 ].address,
        endpoint
    )[ 'validator' ][ 'max-total-delegation' ]
    assert deployed_value == precompile_value == sdk_value, \
            f"Deployedee: {deployed_value}\n" \
            f"Precompile: {precompile_value}\n" \
            f"SDK  Value: {sdk_value}\n"


def test_getSlashingHeightFromBlockForValidator():
    block_number = web3.eth.block_number - 2
    deployed_value = deployed_contract.getSlashingHeightFromBlockForValidator(
        accounts[ 0 ],
        block_number
    )
    precompile_value = read_only_precompile.getSlashingHeightFromBlockForValidator(
        accounts[ 0 ],
        block_number
    )
    assert deployed_value == precompile_value == 0, \
            f"Deployedee: {deployed_value}\n" \
            f"Precompile: {precompile_value}\n" \
            f"Expe Value: 0\n"


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
