//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingContract, Directive } from "./StakingContract.sol";

contract MultipleCallsContract is StakingContract {
  struct Delegation {
    address validator;
    uint256 amount;
  }

  struct Undelegation {
    address validator;
    uint256 amount;
  }

  // given an array of delegations to be made,
  // make them
  // then collect rewards, if any
  function delegateMultipleAndCollectRewards(Delegation[] memory delegations) public returns (bool success) {
    success = true;
    uint256 length = delegations.length;
    Delegation memory delegation;
    for(uint256 i = 0; i < length; i ++) {
      delegation = delegations[i];
      success = _delegate(delegation.validator, delegation.amount) && success;
    }
    success = _collectRewards() && success;
  }

  // undelegate from first and delegate to second (amounts may be unequal)
  // then collect rewards, if any
  function undelegateDelegateAndCollectRewards(Undelegation memory undelegation, Delegation memory delegation) public returns (bool success) {
    success = _undelegate(undelegation.validator, undelegation.amount);
    success = _delegate(delegation.validator, delegation.amount) && success;
    success = _collectRewards() && success;
  }
}
