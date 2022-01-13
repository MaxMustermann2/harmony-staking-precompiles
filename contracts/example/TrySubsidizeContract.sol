//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingPrecompilesSelectors } from "../lib/StakingPrecompiles.sol";

contract TrySubsidizeContract {
  struct Delegation {
    address validator;
    uint256 amount;
  }

  function delegateDelegate(Delegation[] memory delegations) public returns (bool success) {
    success = true;
    uint256 length = delegations.length;
    Delegation memory delegation;
    bytes memory encodedInput;
    bytes32 memPtr;   // do not keep loading it everytime, so declared
    uint256 result;
    assembly {
      memPtr := mload(0x40)
    }
    for(uint256 i = 0; i < length; i ++) {
      delegation = delegations[i];
      encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.Delegate.selector,
                                      msg.sender,
                                      delegation.validator,
                                      delegation.amount);
      assembly {
        result := delegatecall(25000,
          0xfc,
          add(encodedInput, 32),
          mload(encodedInput),
          memPtr,
          0x20
        )
      }
      success = success && result != 0;
    }
  }
}
