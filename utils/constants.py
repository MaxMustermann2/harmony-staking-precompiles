from web3 import Web3
from dotenv import load_dotenv
from os import getenv
from brownie import accounts
from decimal import Decimal
from pyhmy.util import convert_one_to_hex

load_dotenv('.env')
pk = getenv('private_key')
test_net = getenv('test_net')
test_net_shard1 = getenv('test_net_shard1')
w3 = Web3(Web3.HTTPProvider(test_net))
accounts.add(pk)
#derived from pk
# validator_address = '0x8fF9aF553195936502f09A138532f84c7CA70478'
validator_address = 'one13lu674f3jkfk2qhsngfc2vhcf372wprctdjvgu'
validator_info = {
  "name": "Alice",
  "identity": "alice",
  "website": "alice.harmony.one",
  "security-contact": "Bob",
  "details": "Don't mess with me!!!",
  'min-self-delegation': w3.toWei(Decimal('10000'), 'ether'),
  'max-total-delegation': w3.toWei(Decimal('100000'), 'ether'),
  "rate": '0.1',
  "max-rate": '0.9',
  "max-change-rate": '0.05',
  'bls-public-keys': ['0x30b2c38b1316da91e068ac3bd8751c0901ef6c02a1d58bc712104918302c6ed03d5894671d0c816dad2b4d303320f202'],
  'amount': w3.toWei(Decimal( '10000'), 'ether'),   # for now set equal to min
  'bls-key-sigs': ['0x68f800b6adf657b674903e04708060912b893b7c7b500788808247550ab3e186e56a44ebf3ca488f8ed1a42f6cef3a04bd5d2b2b7eb5a767848d3135b362e668ce6bba42c7b9d5666d8e3a83be707b5708e722c58939fe9b07c170f3b7062414']
}
amount = w3.toWei(Decimal('100'), 'ether')
gas_limit = w3.toWei(Decimal('0.00012'), 'gwei')    # trial and error
victim_address = convert_one_to_hex('one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur')
