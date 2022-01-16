//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

abstract contract MigrationPrecompileSelectors {
  function Migrate(address from, address to) public virtual;
}