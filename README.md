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
4. Update `.env` with the node API endpoints, and source it
```bash
source .env
```
5. Add the network to brownie
```bash
brownie networks add live private host=${test_net} chainid=2
```
6. Run `./cleanandtest.sh`

### Project Structure
`StakingContract.sol` implements the `StakingPrecompiles.sol` library, which can be inherited and used to call the staking precompiles from any contract. In other words, a sample contract which uses `StakingPrecompiles.sol` to call the staking precompiles is available as `StakingContract.sol`.

`StakingPrecompiles.sol` uses `abi.encodeWithSelector` and assembly calls in Solidity to call the precompile. These calls require, at maximum, a gas of 25,000 per call, which is what this library uses. In case the precompile throws an error, the entire gas is consumed (as defined in the EVM); if it is successful, only the required gas (21,000 plus data cost) is used.

Other contracts include
 - `MultipleCallsContract.sol` which demonstrates that it is possible to delegate across multiple validators, undelegate, and collect rewards in one single transaction
 - `MaliciousContract.sol` which attempts (but fails) to delegate for another address
 - `ContractWhichReverts.sol`, which makes a delegation and then reverts
 - `TrySubsidizeContract.sol`, which is used to demonstrate that a benevolent contract cannot use assembly `delegatecall` to subsidize the cost of staking transactions for an EOA, that is, the gas used to delegate using the non-EVM staking API is not less than the gas used by the contract

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
1. Delegating, and then reverting the state (`test_contract_which_reverts_success`)
1. Accessing the precompile directly through an EOA, instead of through a contract (`test_eoa_access_success`). Along similar lines, a Contract which uses assembly `delegatecall` has been provided for demonstration to confirm that the precompile does not subsidize non-EVM staking transactions. (`test_eoa_subsidize_success`).

Correctly formed transactions (those which end with `_success` go through), and are part of the tests in this repository.
