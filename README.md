# Staking Precompiles for Harmony
[Gitcoin Bounty](https://gitcoin.co/issue/harmony-one/bounties/77/100026734)

### Running the tests
1. Download required Python dependencies. This repository has been tested with Python3.9
```bash
pip install -r requirements.txt
```
2. Clone the forked harmony repository
```bash
git clone https://github.com/MaxMustermann2/harmony
cd harmony
```
3. Run the (modified) node
```bash
make debug
```
4. Update `.env` with the node API endpoint, and source it (do not change the private key as it is used later)
```bash
source .env
```
5. Add the network to brownie
```bash
brownie networks add live private host=${test_net} chainid=2
```
6. Fund the account using `init.py`
7. Run `cleanandtest.sh`

### Project Structure
`StakingContract.sol` implements the `StakingPrecompiles.sol` library, which can be inherited and used to call the staking precompiles from any contract. In other words, a sample contract which uses `StakingPrecompiles.sol` to call the staking precompiles is available as `StakingContract.sol`.

`StakingPrecompiles.sol` uses `abi.encode` and assembly calls in Solidity to call the precompile. Since Solidity v0.5.0, the leftover gas is directly forwarded to the assembly `call`, and thus, no changes are required to the `gas` variable. It is therefore recommended that the `pragma` of the library not be lowered than v0.5.0

### Integration tests in this repository
The following tests are designed to cover the edge cases of staking, and do not impact the blockchain state.
1. `Delegate` / `Undelegate` without the validator existing
1. `CollectRewards` without delegation
1. `Delegate` with balance < delegation amount
1. `Undelegate` from a non-existing validator
1. `Undelegate` with amount > previously delegated amount
1. `CollectRewards` when there are no other rewards to collect
1. Malicious contracts attempting to `Delegate` / `Undelegate` / `CollectRewards` from accounts other than themselves will result in a failure (`test_delegate_fail_malicious` in `test_staking_contract.py`)
1. Multiple calls to the staking precompile in one transaction (made via Solidity code in `MultipleCallsContract.sol`)
1. Assessing the impact to the block time with maximum possible number of calls to the precompile (`test_many_calls_success`)

Correctly formed transactions (those which end with `_success` go through), and are part of the tests in this repository.
