//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingPrecompiles, Directive } from "../lib/StakingPrecompiles.sol";

contract ContractWhichReverts is StakingPrecompiles {

    event StakingPrecompileCalled(uint8 directive, bool success);

    function acceptMoney() public payable {
    }

    function delegateAndRevert(address validatorAddress, uint256 amount) public returns (bool success) {
        uint256 result = delegate(validatorAddress, amount);
        success = result != 0;
        emit StakingPrecompileCalled(uint8(Directive.DELEGATE), success);
        revert("I will revert");
    }
}
