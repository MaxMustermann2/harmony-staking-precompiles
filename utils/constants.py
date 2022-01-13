from web3 import Web3
from pyhmy import numbers

# https://github.com/harmony-one/harmony/blob/3ab2ea0cda3ef84831396f0c3e8346d03417afb1/core/genesis.go#L135
pk = "1f84c95ac16e6a50f08d44c7bde7aff8742212fda6e4321fde48bf83bef266dc"
validator_address = "one155jp2y76nazx8uw5sa94fr0m4s5aj8e5xm6fu3"
protocol_min_delegation = int( numbers.convert_one_to_atto( 100 ) )
validator_info = {
    "name": "Alice",
    "identity": "alice",
    "website": "alice.harmony.one",
    "security-contact": "Bob",
    "details": "Are you even reading this?",
    "min-self-delegation": int( numbers.convert_one_to_atto( 10000 ) ),
    "max-total-delegation": int( numbers.convert_one_to_atto( 100000 ) ),
    "rate": "0.1",
    "max-rate": "0.9",
    "max-change-rate": "0.05",
    "bls-public-keys": [
        # private key is b1f2a5029f5f43c8c933a61ce936ced030b2c9379f8e2478fc888fa670cdbc89b8cd1ebc29b5b00a81d3152bb3aaa3a337404f50bee5e434430ca3693a94a1c102a765cf3b0887b8b0bcf5317d33f4bec60a97feae2498a39ab7a1c2
        # blspass.txt is empty
        "0xa20e70089664a874b00251c5e85d35a73871531306f3af43e02138339d294e6bb9c4eb82162199c6a852afeaa8d68712",
    ],
    "amount": int( numbers.convert_one_to_atto( 10000 ) ),
    "bls-key-sigs": [
        "0xef2c49a2f31fbbd23c21bc176eaf05cd0bebe6832033075d81fea7cff6f9bc1ab42f3b6895c5493fe645d8379d2eaa1413de55a9d3ce412a4f747cb57d52cc4da4754bfb2583ec9a41fe5dd48287f964f276336699959a5fcef3391dc24df00d",
    ]
}
victim_address = "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur"
spare_validators = [
    "one1ru3p8ff0wsyl7ncsx3vwd5szuze64qz60upg37",
    "one1e8rdglh97t37prtnv7k35ymnh2wazujpzsmzes"
]
spare_validator_infos = [
    {
        "name": "John",
        "identity": "john",
        "website": "john.harmony.one",
        "security-contact": "Someone",
        "details": "Best validator ever",
        "min-self-delegation": int( numbers.convert_one_to_atto( 10000 ) ),
        "max-total-delegation": int( numbers.convert_one_to_atto( 100000 ) ),
        "rate": "0.1",
        "max-rate": "0.9",
        "max-change-rate": "0.05",
        "bls-public-keys": [
            "0xb8c3b3a0f1966c169ca73c348f4b8aee333a407125ab5c67f1d6e1e18ab052ed5fff0f1f7d4a7f789528b5ccd9c47b04",
        ],
        "amount": int( numbers.convert_one_to_atto( 10000 ) ),
        "bls-key-sigs": [
            "0x3de4dff17451fb76a9690efce34bced97dd87eccd371fcd25335826cb879ca21281e82e5c2c76d4ef0ab0fc16e462312628834cbc1f29008b28e16a757367808be85180945b991be3103f98c14c7e3b3e54796d34aab4d8e812d440aa251c419",
        ]
    },
    {
        "name": "Jane",
        "identity": "jane",
        "website": "jane.harmony.one",
        "security-contact": "SomeoneElse",
        "details": "Best validator ever (no, really!)",
        "min-self-delegation": int( numbers.convert_one_to_atto( 10000 ) ),
        "max-total-delegation": int( numbers.convert_one_to_atto( 100000 ) ),
        "rate": "0.1",
        "max-rate": "0.9",
        "max-change-rate": "0.05",
        "bls-public-keys": [
            "0xc52e0e9a0fb25652c64cd0f2aa47d323527730d6905e73126b60bb7499648683dc6993ae40a773c61543c070eccb4288"
        ],
        "amount": int( numbers.convert_one_to_atto( 10000 ) ),
        "bls-key-sigs": [
            "0x30947cd6b0a5f652fac5fcc954d21ad2c5088ba850777bde85e8bdc13a5c38fce612b3c5d5475330dba60281ba8afd0d862c554fff47bd18939f68dcb432f811aa491cdcaabb1b612f1dfe7c8d5e2720e0d93bd61018142990da8937e6c70a03"
        ]
    }
]
spare_validator_pks = [
    "3c86ac59f6b038f584be1c08fced78d7c71bb55d5655f81714f3cddc82144c65",
    "ff9ef6b00a61672b4b7bedd5ac653439b56ac8ee808c99a1bd871cf51b7d60eb"
]
once_gas_limit = 25000  # in wei, per staking tx
once_gas_limit_lower_bound = 21500  # in wei, per staking tx
block_gas_limit = 80000000  # in wei
