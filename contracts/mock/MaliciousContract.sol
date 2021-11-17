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
    bytes32 sizeOfInput;
    uint256 result;
    assembly {
        let memPtr := mload(0x40)
        sizeOfInput := add(mload(encodedInput), 32)
        result := call(0, 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
    }
    success = result != 0;
    emit StakingPrecompileCalled(uint8(Directive.CREATE_VALIDATOR), success);
  }
}
