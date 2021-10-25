//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingPrecompilesSelectors, Directive } from "../lib/StakingPrecompiles.sol";

contract MaliciousContract {
  event StakingPrecompileCalled(uint8 directive, bool success);

  function collectRewards(address victim_address) public returns (uint256 result) {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.CollectRewards.selector,
                                    victim_address);

    bytes32 sizeOfInput;
    assembly {
        let memPtr := mload(0x40)
        sizeOfInput := add(mload(encodedInput), 32)
        result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
    }
    bool success = result != 0;
    emit StakingPrecompileCalled(uint8(Directive.CREATE_VALIDATOR), success);
  }
}
