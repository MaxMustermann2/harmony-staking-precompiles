from pyhmy import transaction
from pyhmy import blockchain
from pyhmy.rpc.exceptions import RPCError, RequestsError
import time
from dotenv import load_dotenv
from os import getenv

load_dotenv('.env')
test_net = getenv('test_net')

initial_funding = [
    {
        # Used by: `account_test_tx`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one1v92y4v2x4q27vzydf8zq62zu9g0jl6z0lx2c8q",
        # scissors matter runway reduce flush illegal ancient absurd scare young copper ticket direct wise person hobby tomato chest edge cost wine crucial vendor elevator
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0x5718a2fda967f051611ccfaf2230dc544c9bdd388f5759a42b2fb0847fc8d759",
        "nonce": "0x0",
        "signed-raw-tx": "0xf86f80843b9aca0082520880809461544ab146a815e6088d49c40d285c2a1f2fe84f8a152d02c7e14af68000008028a076b6130bc018cedb9f8891343fd8982e0d7f923d57ea5250b8bfec9129d4ae22a00fbc01c988d72235b4c71b21ce033d4fc5f82c96710b84685de0578cff075a0a",
    },
    {
        # Used by: `cross_shard_txs`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one1ue25q6jk0xk3dth4pxur9e742vcqfwulhwqh45",
        # obey scissors fiscal hood chaos grit all piano armed change general attract balcony hair cat outside hour quiz unhappy tattoo awful offer toddler invest
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0x28c17c0a2736ba16930ad274e3ecbebea930e82553c7755e0b94c7d7cd1fd6f2",
        "nonce": "0x1",
        "signed-raw-tx": "0xf86f01843b9aca00825208808094e655406a5679ad16aef509b832e7d5533004bb9f8a152d02c7e14af68000008028a0c50737adb507870c2b6f3d9966f096526761730c6b80bd702c114e24aa094ac1a063c0463619123dbe7541687fba70952dab62ba639199750b04cd8902ccb6d615",
    },
    {
        # Used by: `test_get_pending_cx_receipts`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one19l4hghvh40fyldxfznn0a3ss7d5gk0dmytdql4",
        # judge damage safe field faculty piece salon gentle riot unfair symptom sun exclude agree fantasy fossil catalog tool bounce tomorrow churn join very number
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0x6bc3acc3b349edac6d3f563e78990a4566192d6fdab93814ea29ae9157d4085b",
        "nonce": "0x2",
        "signed-raw-tx": "0xf86f02843b9aca008252088080942feb745d97abd24fb4c914e6fec610f3688b3dbb8a152d02c7e14af68000008027a0abfa0480b878ca798a17e88251109761ed1d281f1da92faa21b6e456ad558774a016b460ec602b08f06a2845478269b1014b5491bdc0993988ca39f689b2405992",
    },
    {
        # Used by: `test_pending_transactions_v1`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one1twhzfc2wr4j5ka7gs9pmllpnrdyaskcl5lq8ye",
        # science swim absent horse gas wink switch section soup pair chuckle rug paddle lottery message veteran poverty alone current prize spoil dune super crumble
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0xdcd7870635acd3fb1e962c76f2e3cddbeb421238fcf702e3d1fa42ca6de434b2",
        "nonce": "0x3",
        "signed-raw-tx": "0xf86f03843b9aca008252088080945bae24e14e1d654b77c88143bffc331b49d85b1f8a152d02c7e14af68000008027a0356e6bfd8718c7102f0d94fdb8be1cba090daf44c71086f9817de3b264cb54c2a052c8781691dce63997ca4f765adec7b351a9a23a80a97bcf238ccbdf8a71f71f",
    },
    {
        # Used by: `test_pending_transactions_v2`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one1u57rlv5q82deja6ew2l9hdy7ag3dwnw57x8s9t",
        # noble must all evoke core grass goose describe latin left because awful gossip tuna broccoli tomorrow piece enable theme comic below avoid dove high
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0xa8a678243fffcfc16ff8f35315094aafc029175b962ec595f7c71efce4a47c8a",
        "nonce": "0x4",
        "signed-raw-tx": "0xf86f04843b9aca00825208808094e53c3fb2803a9b99775972be5bb49eea22d74dd48a152d02c7e14af68000008028a0d2f061075852ee5b2572b18e8879d5656e8660113d88f2b806961b25312e5ae1a078004b6b332f09b1a53c3cbad6fd427fa57b0b368ae2126e458b9622d1668edf",
    },
    {
        # Used by: `test_send_raw_transaction_v1`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one1p5x4t7mvd94jn5awxmhlvgqmlazx5egzz7rveg",
        # mushroom penalty pulse blouse horror into color call grace observe famous bridge consider universe uncle horror people tank useless alley uncover emotion next ke
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0x1d0d4111d9f5d2d28e85d5ebd1460944e8d328df45a2bbfae1de309c3a6cf632",
        "nonce": "0x5",
        "signed-raw-tx": "0xf86f05843b9aca008252088080940d0d55fb6c696b29d3ae36eff6201bff446a65028a152d02c7e14af68000008027a06dee240ff456073c11fd093e24ba29eda88e00cd710c05d83c855cce1aff47a2a06bf74d512215a2ec02fb5034a1e344901706387e72ce08b5a37a2f434717f859",
    },
    {
        # Used by: `test_send_raw_transaction_v2`
        "from": "one1zksj3evekayy90xt4psrz8h6j2v3hla4qwz4ur",
        "to": "one13lu674f3jkfk2qhsngfc2vhcf372wprctdjvgu",
        # organ truly miss sell visual pulse maid element slab sugar bullet absorb digital space dance long another man cherry fruit effort pluck august flag
        "amount": "100000",
        "from-shard": 0,
        "to-shard": 0,
        "hash": "0x855e230866377e00a56ae6958c8acfe6f0d19f8e71a0c323d92794aeda5c6bc8",
        "nonce": "0x6",
        "signed-raw-tx": "0xf86f06843b9aca008252088080948ff9af553195936502f09a138532f84c7ca704788a152d02c7e14af68000008028a01a4c6dbc9177cf9057de09d4f654950a38aba83e98502d59b478f899b196c4aaa00652c34a53082aee876713954ce70a21288c3727c29fb9c729ce10f19d106370",
    }
]
print("Waiting for node to start producing blocks")
current_block_num = 0
timeout = 60
start_time = time.time()
while((current_block_num==0) and (time.time() - start_time) <= timeout):
    try:
        current_block_num = blockchain.get_block_number(test_net)
        print(current_block_num)
        start_time = time.time()
    except (RPCError, RequestsError):
        continue
    time.sleep(1)
if current_block_num > 0:
    print("First block has been produced, moving ahead")
    print("Undertaking initial funding")
    hashes = []
    for tx in initial_funding:
        hashes.append(transaction.send_raw_transaction(tx['signed-raw-tx'], endpoint=test_net))
    for hash in hashes:
        tx_response = transaction.get_transaction_by_hash(hash, endpoint=test_net)
        if tx_response is not None:
            if tx_response[ 'blockHash' ] != '0x0000000000000000000000000000000000000000000000000000000000000000':
                continue
    print("Done")
else:
    print("Fuck off")
