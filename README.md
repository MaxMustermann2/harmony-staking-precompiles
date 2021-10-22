# Staking Precompiles for Harmony
[Gitcoin Bounty](https://gitcoin.co/issue/harmony-one/bounties/77/100026734)

### Running the tests
1. Download required python dependencies
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

`StakingPrecompiles.sol` uses `abi.encode` and assembly calls in Solidity to call the precompile. Since Solidity v0.5.0, the leftover gas is directly forwarded to the assembly `Call`, and thus, no changes are required to the `gas` variable. It is recommended that the `pragma` of the library not be lowered than v0.5.0

### Integration tests in this repository
The following tests are designed to cover the edge cases of staking, and do not impact the blockchain state.
1. `Delegate` / `Undelegate` / `EditValidator` without the validator existing
2. `CollectRewards` without delegation
3. `CreateValidator` without funding the account
4. `CreateValidator` with missing `Description` / `CommissionRates` subfields
5. `CreateValidator` with low `MinSelfDelegation`, and `MaxTotalDelegation` > `MinSelfDelegation`
6. `CreateValidator` with incorrect length for `SlotPubKey` or `SlotKeySig`, or mismatch between `SlotPubKey` and `SlotKeySig`
7. `CreateValidator` with current delegation `Amount` < `MinSelfDelegation`
8. `CreateValidator` with long text in `Description`
9. Attempting to create a validator at an already existing validator's address
10. `CreateValidator` with the same identity or BLS key as another validator
11. `EditValidator` with missing `Description` subfield
12. `EditValidator` with `CommissionRate` > `MaxRate`
13. `EditValidator` with a `SlotKeyToRemove` that doesn't exist
14. `EditValidator` with signature mismatch between `SlotKeyToAdd` and `SlotKeyToAddSig`
15. `Delegate` with balance < delegation amount
16. `Undelegate` from a non-existing validator
17. `Undelegate` with amount > previously delegated amount
18. `CollectRewards` when there are no other rewards to collect
19. Malicious contracts attempting to `CreateValidator` / `EditValidator` / `Delegate` / `Undelegate` / `CollectRewards` from accounts other than themselves will result in a failure (`malicious_collect_rewards_fail_to_collect_others_rewards` in `test_staking_contract.py`)

Correctly formed transactions (those which end with `_success` go through), and are part of the tests in this repository.
