//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

contract StakingPrecompiles {
    //0 => createValidator
    //1 => editValidator
    //2 => delegate
    //3 => unDelegate
    //4 => collectRewards
    enum Directive{
        CREATE_VALIDATOR,
        EDIT_VALIDATOR,
        DELEGATE,
        UNDELEGATE,
        COLLECT_REWARDS
    }

    struct Description {
        string name;
        string identity;
        string website;
        string securityContact;
        string details;
    }

    struct CommissionRate {
        string rate;
        string maxRate;
        string maxChangeRate;
    }

    function createValidator(Description memory description,
                              CommissionRate memory commission,
                              uint256 minSelfDelegation,
                              uint256 maxTotalDelegation,
                              bytes[] memory slotPubKeys,
                              bytes[] memory slotKeySigs,
                              uint256 amount)
                            public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.CREATE_VALIDATOR),
                                        address(this),
                                        description,
                                        commission,
                                        minSelfDelegation,
                                        maxTotalDelegation,
                                        slotPubKeys,
                                        slotKeySigs,
                                        amount);
        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }

    function editValidator(Description memory description,
                          string memory commissionRate,
                          uint256 minSelfDelegation,
                          uint256 maxTotalDelegation,
                          bytes memory slotKeyToRemove,
                          bytes memory slotKeyToAdd,
                          bytes memory slotKeyToAddSig)
                        public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.EDIT_VALIDATOR), address(this), description, commissionRate, minSelfDelegation, maxTotalDelegation, slotKeyToRemove, slotKeyToAdd, slotKeyToAddSig);

        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }

    function delegate(address validatorAddress, uint256 amount) public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.DELEGATE), address(this), validatorAddress, amount);
        //bytes memory encodedInput = abi.encodePacked(uint8(Directive.DELEGATE), encodedInput1);

        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }

    function undelegate(address validatorAddress, uint256 amount) public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.UNDELEGATE), address(this), validatorAddress, amount);

        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }

    function collectRewards() public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.COLLECT_REWARDS), address(this));

        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }

}
