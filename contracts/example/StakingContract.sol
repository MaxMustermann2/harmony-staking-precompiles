//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

import { StakingPrecompiles } from "../lib/StakingPrecompiles.sol";

contract StakingContract is StakingPrecompiles {

    event StakingPrecompileCalled(uint8 directive, bool success);

    function acceptMoney() public payable {
    }

    function _createValidator(Description memory description,
                              CommissionRate memory commissionRate,
                              uint256 minSelfDelegation,
                              uint256 maxTotalDelegation,
                              bytes[] memory slotPubKeys,
                              bytes[] memory slotKeySigs,
                              uint256 amount)
                            public returns (bool success) {
         uint256 result = createValidator(description, commissionRate, minSelfDelegation, maxTotalDelegation, slotPubKeys, slotKeySigs, amount);
         success = result != 0;
         emit StakingPrecompileCalled(uint8(Directive.CREATE_VALIDATOR), success);
    }

    function _editValidator(Description memory description,
                          string memory commissionRate,
                          uint256 minSelfDelegation,
                          uint256 maxTotalDelegation,
                          bytes memory slotKeyToRemove,
                          bytes memory slotKeyToAdd, bytes memory slotKeyToAddSig) public returns (bool success) {
        uint256 result = editValidator(description, commissionRate, minSelfDelegation, maxTotalDelegation, slotKeyToRemove, slotKeyToAdd, slotKeyToAddSig);
        success = result != 0;
        emit StakingPrecompileCalled(uint8(Directive.EDIT_VALIDATOR), success);
    }

    function _delegate(address validatorAddress, uint256 amount) public returns (bool success) {
        uint256 result = delegate(validatorAddress, amount);
        success = result != 0;
        emit StakingPrecompileCalled(uint8(Directive.DELEGATE), success);
    }

    function _undelegate(address validatorAddress, uint256 amount) public returns (bool success) {
        uint256 result = undelegate(validatorAddress, amount);
        success = result != 0;
        emit StakingPrecompileCalled(uint8(Directive.UNDELEGATE), success);
    }

    function _collectRewards() public returns (bool success) {
        uint256 result = collectRewards();
        success = result != 0;
        emit StakingPrecompileCalled(uint8(Directive.COLLECT_REWARDS), success);
    }
}
