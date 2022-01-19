//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

enum Directive {
  CREATE_VALIDATOR, // unused
  EDIT_VALIDATOR,   // unused
  DELEGATE,
  UNDELEGATE,
  COLLECT_REWARDS
}

abstract contract StakingPrecompilesSelectors {
  function Delegate(address delegatorAddress,
                    address validatorAddress,
                    uint256 amount) public virtual;
  function Undelegate(address delegatorAddress,
                      address validatorAddress,
                      uint256 amount) public virtual;
  function CollectRewards(address delegatorAddress) public virtual;
  function Migrate(address from, address to) public virtual;
}

contract StakingPrecompiles {
  function delegate(address validatorAddress, uint256 amount) public returns (uint256 result) {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.Delegate.selector,
                                    address(this),
                                    validatorAddress,
                                    amount);
    assembly {
      // we estimate a gas consumption of 25k per precompile
      result := call(25000,
        0xfc,
        0x0,
        add(encodedInput, 32),
        mload(encodedInput),
        mload(0x40),
        0x20
      )
    }
  }

  function undelegate(address validatorAddress, uint256 amount) public returns (uint256 result) {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.Undelegate.selector,
                                    address(this),
                                    validatorAddress,
                                    amount);
    assembly {
      // we estimate a gas consumption of 25k per precompile
      result := call(25000,
        0xfc,
        0x0,
        add(encodedInput, 32),
        mload(encodedInput),
        mload(0x40),
        0x20
      )
    }
  }

  function collectRewards() public returns (uint256 result) {
    bytes memory encodedInput = abi.encodeWithSelector(StakingPrecompilesSelectors.CollectRewards.selector,
                                    address(this));
    assembly {
      // we estimate a gas consumption of 25k per precompile
      result := call(25000,
        0xfc,
        0x0,
        add(encodedInput, 32),
        mload(encodedInput),
        mload(0x40),
        0x20
      )
    }
  }

  function epoch() public view returns (uint256) {
    bytes32 input;
    bytes32 epochNumber;
    assembly {
      let memPtr := mload(0x40)
      if iszero(staticcall(not(0), 0xfb, input, 32, memPtr, 32)) {
          invalid()
      }
      epochNumber := mload(memPtr)
    }
    return uint256(epochNumber);
  }

}
