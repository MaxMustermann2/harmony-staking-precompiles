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
gas_limit = w3.toWei(Decimal('0.000025'), 'gwei')    # staking transactions take between 22-25k
victim_address = convert_one_to_hex('one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur')

spare_validators = [ 'one1ru3p8ff0wsyl7ncsx3vwd5szuze64qz60upg37',
                    'one1e8rdglh97t37prtnv7k35ymnh2wazujpzsmzes' ]
spare_validator_infos = [ {
    'name': 'John',
    'identity': 'john',
    'website': 'john.harmony.one',
    'security-contact': 'Someone',
    'details': 'Best validator ever',
    'min-self-delegation': w3.toWei(Decimal('10000'), 'ether'),
    'max-total-delegation': w3.toWei(Decimal('100000'), 'ether'),
    "rate": '0.1',
    "max-rate": '0.9',
    "max-change-rate": '0.05',
    'bls-public-keys': ['0xb8c3b3a0f1966c169ca73c348f4b8aee333a407125ab5c67f1d6e1e18ab052ed5fff0f1f7d4a7f789528b5ccd9c47b04'],
    'amount': w3.toWei(Decimal( '10000'), 'ether'),   # for now set equal to min
    'bls-key-sigs': ['0x3de4dff17451fb76a9690efce34bced97dd87eccd371fcd25335826cb879ca21281e82e5c2c76d4ef0ab0fc16e462312628834cbc1f29008b28e16a757367808be85180945b991be3103f98c14c7e3b3e54796d34aab4d8e812d440aa251c419']
 }, {
    'name': 'Jane',
    'identity': 'jane',
    'website': 'jane.harmony.one',
    'security-contact': 'SomeoneElse',
    'details': 'Best validator ever (no, really!)',
    'min-self-delegation': w3.toWei(Decimal('10000'), 'ether'),
    'max-total-delegation': w3.toWei(Decimal('100000'), 'ether'),
    "rate": '0.1',
    "max-rate": '0.9',
    "max-change-rate": '0.05',
    'bls-public-keys': ['0xc52e0e9a0fb25652c64cd0f2aa47d323527730d6905e73126b60bb7499648683dc6993ae40a773c61543c070eccb4288'],
    'amount': w3.toWei(Decimal( '10000'), 'ether'),   # for now set equal to min
    'bls-key-sigs': ['0x30947cd6b0a5f652fac5fcc954d21ad2c5088ba850777bde85e8bdc13a5c38fce612b3c5d5475330dba60281ba8afd0d862c554fff47bd18939f68dcb432f811aa491cdcaabb1b612f1dfe7c8d5e2720e0d93bd61018142990da8937e6c70a03']
 } ]
spare_validator_pks = ['3c86ac59f6b038f584be1c08fced78d7c71bb55d5655f81714f3cddc82144c65',
        'ff9ef6b00a61672b4b7bedd5ac653439b56ac8ee808c99a1bd871cf51b7d60eb'
    ]
