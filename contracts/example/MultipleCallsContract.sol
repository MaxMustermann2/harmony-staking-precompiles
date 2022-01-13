//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingContract } from "./StakingContract.sol";
import { StakingPrecompilesSelectors } from "../lib/StakingPrecompiles.sol";

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

  // call multiple times to see the block speed
  // assembly is used directly to save gas
  // allowing for larger number of calls
  function multipleCollectRewards(uint256 howMany) public {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.CollectRewards.selector,
                                    address(this));
    bytes32 sizeOfInput;
    bytes32 memPtr;
    uint256 ignored;
    assembly {
      sizeOfInput := mload(encodedInput)
      memPtr := mload(0x40)
    }
    for(uint256 i = 0; i < howMany; i ++) {
      assembly {
        ignored := call(25000,
          0xfc,
          0x0,
          add(encodedInput, 32),
          sizeOfInput,
          memPtr,
          0x20
        )
      }
    }
  }
}
