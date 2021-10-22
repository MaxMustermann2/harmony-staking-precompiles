from web3 import Web3
from dotenv import load_dotenv
from os import getenv
from brownie import accounts
from decimal import Decimal

load_dotenv('.env')
pk = getenv('private_key')
test_net = getenv('test_net')
w3 = Web3(Web3.HTTPProvider(test_net))
accounts.add(pk)
# validatorAddress = stakingContract.address
description = {
  "name": "Alice",
  "identity": "alice",
  "website": "alice.harmony.one",
  "securityContact": "Bob",
  "details": "Don't mess with me!!!"
}
newDescription = {
  "name": "Bob",
  "identity": "bob",
  "website": "bob.harmony.one",
  "securityContact": "Alice",
  "details": "Don't mess with me!!!"
}
commissionRates = {
  "rate": '0.1',
  "maxRate": '0.9',
  "maxChangeRate": '0.05'
}

minSelfDelegation = w3.toWei(Decimal('10000'), 'ether')
maxTotalDelegation = w3.toWei(Decimal('100000'), 'ether')
slotPubKeys = ['0x30b2c38b1316da91e068ac3bd8751c0901ef6c02a1d58bc712104918302c6ed03d5894671d0c816dad2b4d303320f202']
slotKeySigs = ['0x68f800b6adf657b674903e04708060912b893b7c7b500788808247550ab3e186e56a44ebf3ca488f8ed1a42f6cef3a04bd5d2b2b7eb5a767848d3135b362e668ce6bba42c7b9d5666d8e3a83be707b5708e722c58939fe9b07c170f3b7062414']

slotPubKeysOfIncorrectLength = ['0x30b2c38b1316da91e068ac3bd8751c0901ef6c02a1d58bc712104918302c6ed03d5894671d0c816dad2b4d3033']
slotKeySigsOfIncorrectLength = ['0x68f800b6adf657b674903e04708060912b893b7c7b500788808247550ab3e186e56a44ebf3ca488f8ed1a42f6cef3a04bd5d2b2b7eb5a767848d3135b362e668ce6bba42c7b9d5666d8e3a83be707b5708e722c58939fe9b07c170f3b70624']
slotKeySigsIncorrect         = ['0x69f800b6adf657b674903e04708060912b893b7c7b500788808247550ab3e186e56a44ebf3ca488f8ed1a42f6cef3a04bd5d2b2b7eb5a767848d3135b362e668ce6bba42c7b9d5666d8e3a83be707b5708e722c58939fe9b07c170f3b7062414']

amount = w3.toWei(Decimal('100'), 'ether')

description_with_invalid_details = {
  "name": "Alice",
  "identity": "alice",
  "website": "alice.harmony.one",
  "securityContact": "Bob",
  "details": "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum"
}

new_description_with_previous_identity = {
  "name": "Bob",
  "identity": "alice",
  "website": "bob.harmony.one",
  "securityContact": "Alice",
  "details": "Don't mess with me!!!"
}

incorrect_slot_key = '0xb9486167ab9087ab818dc4ce026edb5bf216863364c32e42df2af03c5ced1ad181e7d12f0e6dd5307a73b62247608611'
