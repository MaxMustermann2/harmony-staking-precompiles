// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

abstract contract RoStakingPrecompileSelectors {
  function getDelegationByDelegatorAndValidator(address delegatorAddress,
            address validatorAddress) public view virtual returns (uint256);
  function getValidatorCommissionRate(address validatorAddress) 
            public view virtual returns (uint256);
  function getValidatorMaxTotalDelegation(address validatorAddress)
            public view virtual returns (uint256);
  function getValidatorTotalDelegation(address validatorAddress)
            public view virtual returns (uint256);
  function getBalanceAvailableForRedelegation(address delegatorAddress)
            public view virtual returns (uint256);
  function getSlashingHeightFromBlockForValidator(address validatorAddress,
            uint256 blockNumber) public view virtual returns (uint256);
}

contract ReadOnlyStakingPrecompile {
    function getDelegationByDelegatorAndValidator(address delegatorAddress, 
    address validatorAddress) public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getDelegationByDelegatorAndValidator.selector,
            delegatorAddress, validatorAddress);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }

    // since Solidity doesn't support floats directly, these returns
    // the commission rate * 1e18 (the node takes care of precision etc)
    // for example, 0.1 is 100000000000000000
    function getValidatorCommissionRate(address validatorAddress)
    public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getValidatorCommissionRate.selector,
            validatorAddress);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }

    function getValidatorMaxTotalDelegation(address validatorAddress)
    public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getValidatorMaxTotalDelegation.selector,
            validatorAddress);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }

    function getValidatorTotalDelegation(address validatorAddress)
    public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getValidatorTotalDelegation.selector,
            validatorAddress);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }

    function getBalanceAvailableForRedelegation(address delegatorAddress)
    public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getBalanceAvailableForRedelegation.selector,
            delegatorAddress);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }

    function getSlashingHeightFromBlockForValidator(address validatorAddress,
    uint256 blockNumber) public view returns (uint256 result) {
        bytes memory encodedInput = abi.encodeWithSelector(
            RoStakingPrecompileSelectors.getSlashingHeightFromBlockForValidator.selector,
            validatorAddress, blockNumber);
        assembly {
            let memPtr := mload(0x40)
            if iszero(staticcall(not(0),
                0xFA,
                add(encodedInput, 0x20),
                mload(encodedInput),
                memPtr,
                0x20
            )) {
                invalid()
            }
            result := mload(memPtr)
        }
    }
}