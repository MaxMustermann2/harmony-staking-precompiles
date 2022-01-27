const { ContractFactory } = require( '@harmony-js/contract' );
const { Wallet } = require( '@harmony-js/account' );
const { Messenger, HttpProvider } = require( '@harmony-js/network' );
const { ChainID, ChainType, hexToNumber, toWei, Units } = require( '@harmony-js/utils' );
// read endpoint from .env
require( 'dotenv' ).config();
const endpoint = process.env.endpoint;
const pk = '1f84c95ac16e6a50f08d44c7bde7aff8742212fda6e4321fde48bf83bef266dc';

// load abi and contract object
const wallet = new Wallet(
  new Messenger(
    new HttpProvider( endpoint ),
    ChainType.Harmony,
    ChainID.HmyLocal,
  ),
);
const factory = new ContractFactory( wallet );
const contractJson = require( '../build/contracts/StakingPrecompilesSelectors.json' );
const contract = factory.createContract( contractJson.abi, '0x00000000000000000000000000000000000000FC' );
contract.wallet.addByPrivateKey( pk );

contract.methods.Delegate(
  '0xA5241513DA9F4463F1d4874b548dFBAC29D91f34', // delegator address
  '0xA5241513DA9F4463F1d4874b548dFBAC29D91f34', // validator address
  toWei( 100, Units.one ),                      // amount
).send(
    {
      gasPrice: toWei( 30, Units.Gwei ),        // network gas limit
      gasLimit: 46000                           // ~23k for base + 23k for staking tx
    }
).then( response => {
  console.log( response );
} );