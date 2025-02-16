"""A web3.py Contract class for the ForwarderFactory contract.

DO NOT EDIT.  This file was generated by pypechain.  See documentation at
https://github.com/delvtech/pypechain"""

# contracts have PascalCase names
# pylint: disable=invalid-name

# contracts control how many attributes and arguments we have in generated code
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

# we don't need else statement if the other conditionals all have return,
# but it's easier to generate
# pylint: disable=no-else-return

# This file is bound to get very long depending on contract sizes.
# pylint: disable=too-many-lines

# methods are overriden with specific arguments instead of generic *args, **kwargs
# pylint: disable=arguments-differ

from __future__ import annotations

from typing import Any, NamedTuple, Type, cast

from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from typing_extensions import Self
from web3 import Web3
from web3.contract.contract import Contract, ContractConstructor, ContractFunction, ContractFunctions
from web3.exceptions import FallbackNotFound
from web3.types import ABI, BlockIdentifier, CallOverride, TxParams

from .utilities import dataclass_to_tuple, rename_returned_types

structs = {}


class ForwarderFactoryERC20LINK_HASHContractFunction(ContractFunction):
    """ContractFunction for the ERC20LINK_HASH method."""

    def __call__(self) -> ForwarderFactoryERC20LINK_HASHContractFunction:  # type: ignore
        clone = super().__call__()
        self.kwargs = clone.kwargs
        self.args = clone.args
        return self

    def call(
        self,
        transaction: TxParams | None = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride | None = None,
        ccip_read_enabled: bool | None = None,
    ) -> bytes:
        """returns bytes."""
        # Define the expected return types from the smart contract call

        return_types = bytes

        # Call the function

        raw_values = super().call(transaction, block_identifier, state_override, ccip_read_enabled)
        return cast(bytes, rename_returned_types(structs, return_types, raw_values))


class ForwarderFactoryCreateContractFunction(ContractFunction):
    """ContractFunction for the create method."""

    def __call__(self, token: str, tokenId: int) -> ForwarderFactoryCreateContractFunction:  # type: ignore
        clone = super().__call__(dataclass_to_tuple(token), dataclass_to_tuple(tokenId))
        self.kwargs = clone.kwargs
        self.args = clone.args
        return self

    def call(
        self,
        transaction: TxParams | None = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride | None = None,
        ccip_read_enabled: bool | None = None,
    ) -> str:
        """returns str."""
        # Define the expected return types from the smart contract call

        return_types = str

        # Call the function

        raw_values = super().call(transaction, block_identifier, state_override, ccip_read_enabled)
        return cast(str, rename_returned_types(structs, return_types, raw_values))


class ForwarderFactoryGetDeployDetailsContractFunction(ContractFunction):
    """ContractFunction for the getDeployDetails method."""

    class ReturnValues(NamedTuple):
        """The return named tuple for GetDeployDetails."""

        arg1: str
        arg2: int

    def __call__(self) -> ForwarderFactoryGetDeployDetailsContractFunction:  # type: ignore
        clone = super().__call__()
        self.kwargs = clone.kwargs
        self.args = clone.args
        return self

    def call(
        self,
        transaction: TxParams | None = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride | None = None,
        ccip_read_enabled: bool | None = None,
    ) -> ReturnValues:
        """returns ReturnValues."""
        # Define the expected return types from the smart contract call

        return_types = [str, int]

        # Call the function

        raw_values = super().call(transaction, block_identifier, state_override, ccip_read_enabled)
        return self.ReturnValues(*rename_returned_types(structs, return_types, raw_values))


class ForwarderFactoryGetForwarderContractFunction(ContractFunction):
    """ContractFunction for the getForwarder method."""

    def __call__(self, token: str, tokenId: int) -> ForwarderFactoryGetForwarderContractFunction:  # type: ignore
        clone = super().__call__(dataclass_to_tuple(token), dataclass_to_tuple(tokenId))
        self.kwargs = clone.kwargs
        self.args = clone.args
        return self

    def call(
        self,
        transaction: TxParams | None = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride | None = None,
        ccip_read_enabled: bool | None = None,
    ) -> str:
        """returns str."""
        # Define the expected return types from the smart contract call

        return_types = str

        # Call the function

        raw_values = super().call(transaction, block_identifier, state_override, ccip_read_enabled)
        return cast(str, rename_returned_types(structs, return_types, raw_values))


class ForwarderFactoryContractFunctions(ContractFunctions):
    """ContractFunctions for the ForwarderFactory contract."""

    ERC20LINK_HASH: ForwarderFactoryERC20LINK_HASHContractFunction

    create: ForwarderFactoryCreateContractFunction

    getDeployDetails: ForwarderFactoryGetDeployDetailsContractFunction

    getForwarder: ForwarderFactoryGetForwarderContractFunction

    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: ChecksumAddress | None = None,
        decode_tuples: bool | None = False,
    ) -> None:
        super().__init__(abi, w3, address, decode_tuples)
        self.ERC20LINK_HASH = ForwarderFactoryERC20LINK_HASHContractFunction.factory(
            "ERC20LINK_HASH",
            w3=w3,
            contract_abi=abi,
            address=address,
            decode_tuples=decode_tuples,
            function_identifier="ERC20LINK_HASH",
        )
        self.create = ForwarderFactoryCreateContractFunction.factory(
            "create",
            w3=w3,
            contract_abi=abi,
            address=address,
            decode_tuples=decode_tuples,
            function_identifier="create",
        )
        self.getDeployDetails = ForwarderFactoryGetDeployDetailsContractFunction.factory(
            "getDeployDetails",
            w3=w3,
            contract_abi=abi,
            address=address,
            decode_tuples=decode_tuples,
            function_identifier="getDeployDetails",
        )
        self.getForwarder = ForwarderFactoryGetForwarderContractFunction.factory(
            "getForwarder",
            w3=w3,
            contract_abi=abi,
            address=address,
            decode_tuples=decode_tuples,
            function_identifier="getForwarder",
        )


forwarderfactory_abi: ABI = cast(
    ABI,
    [
        {
            "type": "function",
            "name": "ERC20LINK_HASH",
            "inputs": [],
            "outputs": [{"name": "", "type": "bytes32", "internalType": "bytes32"}],
            "stateMutability": "view",
        },
        {
            "type": "function",
            "name": "create",
            "inputs": [
                {"name": "__token", "type": "address", "internalType": "contract IMultiToken"},
                {"name": "__tokenId", "type": "uint256", "internalType": "uint256"},
            ],
            "outputs": [{"name": "", "type": "address", "internalType": "contract ERC20Forwarder"}],
            "stateMutability": "nonpayable",
        },
        {
            "type": "function",
            "name": "getDeployDetails",
            "inputs": [],
            "outputs": [
                {"name": "", "type": "address", "internalType": "contract IMultiToken"},
                {"name": "", "type": "uint256", "internalType": "uint256"},
            ],
            "stateMutability": "view",
        },
        {
            "type": "function",
            "name": "getForwarder",
            "inputs": [
                {"name": "__token", "type": "address", "internalType": "contract IMultiToken"},
                {"name": "__tokenId", "type": "uint256", "internalType": "uint256"},
            ],
            "outputs": [{"name": "", "type": "address", "internalType": "address"}],
            "stateMutability": "view",
        },
        {"type": "error", "name": "InvalidForwarderAddress", "inputs": []},
    ],
)
# pylint: disable=line-too-long
forwarderfactory_bytecode = HexStr(
    "0x6080604052600080546001600160a01b0319166001908117909155805534801561002857600080fd5b506115e9806100386000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c80630710fd58146100515780630ecaea7314610081578063600eb4ba14610094578063d13053bb146100ca575b600080fd5b61006461005f3660046102cc565b6100e0565b6040516001600160a01b0390911681526020015b60405180910390f35b61006461008f3660046102cc565b6101b5565b6100ab6000546001546001600160a01b0390911691565b604080516001600160a01b039093168352602083019190915201610078565b6100d2610292565b604051908152602001610078565b604080516001600160a01b03841660208201529081018290526000908190606001604051602081830303815290604052805190602001209050600060ff60f81b308360405180602001610132906102bf565b6020820181038252601f19601f820116604052508051906020012060405160200161019494939291906001600160f81b031994909416845260609290921b6bffffffffffffffffffffffff191660018401526015830152603582015260550190565b60408051808303601f19018152919052805160209091012095945050505050565b6001819055600080546001600160a01b0319166001600160a01b038416908117825560408051602081019290925281018390528190606001604051602081830303815290604052805190602001209050600081604051610214906102bf565b8190604051809103906000f5905080158015610234573d6000803e3d6000fd5b50905061024185856100e0565b6001600160a01b0316816001600160a01b0316146102715760405162e0775560e61b815260040160405180910390fd5b600080546001600160a01b0319166001908117909155805591505092915050565b6040516102a1602082016102bf565b6020820181038252601f19601f820116604052508051906020012081565b6112af8061030583390190565b600080604083850312156102df57600080fd5b82356001600160a01b03811681146102f657600080fd5b94602093909301359350505056fe60e06040523480156200001157600080fd5b50604080516330075a5d60e11b815281513392839263600eb4ba926004808301939282900301816000875af11580156200004f573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906200007591906200019c565b60a08190526001600160a01b039091166080819052604051622b600360e21b81527f8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f9262ad800c91620000cf919060040190815260200190565b600060405180830381865afa158015620000ed573d6000803e3d6000fd5b505050506040513d6000823e601f3d908101601f19168201604052620001179190810190620001ee565b805160209182012060408051808201825260018152603160f81b90840152805192830193909352918101919091527fc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc660608201524660808201523060a082015260c00160408051601f19818403018152919052805160209091012060c05250620002c3565b60008060408385031215620001b057600080fd5b82516001600160a01b0381168114620001c857600080fd5b6020939093015192949293505050565b634e487b7160e01b600052604160045260246000fd5b600060208083850312156200020257600080fd5b82516001600160401b03808211156200021a57600080fd5b818501915085601f8301126200022f57600080fd5b815181811115620002445762000244620001d8565b604051601f8201601f19908116603f011681019083821181831017156200026f576200026f620001d8565b8160405282815288868487010111156200028857600080fd5b600093505b82841015620002ac57848401860151818501870152928501926200028d565b600086848301015280965050505050505092915050565b60805160a05160c051610f306200037f600039600081816101c601526108fc015260008181610140015281816102ab0152818161035f0152818161045d015281816105080152818161061a015281816106cf0152818161073e01528181610a030152610bab015260008181610263015281816102d4015281816103a5015281816104860152818161055601528181610653015281816106f80152818161078e01528181610a4001528181610b210152610be90152610f306000f3fe608060405234801561001057600080fd5b50600436106100f55760003560e01c80633644e51511610097578063a9059cbb11610066578063a9059cbb14610223578063d505accf14610236578063dd62ed3e1461024b578063fc0c546a1461025e57600080fd5b80633644e515146101c157806370a08231146101e85780637ecebe00146101fb57806395d89b411461021b57600080fd5b806318160ddd116100d357806318160ddd1461017057806323b872dd1461017857806330adf81f1461018b578063313ce567146101b257600080fd5b806306fdde03146100fa578063095ea7b31461011857806317d70f7c1461013b575b600080fd5b61010261029d565b60405161010f9190610c7f565b60405180910390f35b61012b610126366004610cce565b610350565b604051901515815260200161010f565b6101627f000000000000000000000000000000000000000000000000000000000000000081565b60405190815260200161010f565b61016261044e565b61012b610186366004610cf8565b6104f9565b6101627f6e71edae12b1b97f4d1f60370fef10105fa2faae0126114a169c64845d6126c981565b6040516012815260200161010f565b6101627f000000000000000000000000000000000000000000000000000000000000000081565b6101626101f6366004610d34565b61060b565b610162610209366004610d34565b60006020819052908152604090205481565b6101026106c0565b61012b610231366004610cce565b61072f565b610249610244366004610d56565b610829565b005b610162610259366004610dc9565b610af7565b6102857f000000000000000000000000000000000000000000000000000000000000000081565b6040516001600160a01b03909116815260200161010f565b604051622b600360e21b81527f000000000000000000000000000000000000000000000000000000000000000060048201526060907f00000000000000000000000000000000000000000000000000000000000000006001600160a01b03169062ad800c906024015b600060405180830381865afa158015610323573d6000803e3d6000fd5b505050506040513d6000823e601f3d908101601f1916820160405261034b9190810190610e12565b905090565b6040516313b4b5ab60e21b81527f000000000000000000000000000000000000000000000000000000000000000060048201526001600160a01b038381166024830152604482018390523360648301526000917f000000000000000000000000000000000000000000000000000000000000000090911690634ed2d6ac90608401600060405180830381600087803b1580156103eb57600080fd5b505af11580156103ff573d6000803e3d6000fd5b50506040518481526001600160a01b03861692503391507f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925906020015b60405180910390a35060015b92915050565b60405163bd85b03960e01b81527f000000000000000000000000000000000000000000000000000000000000000060048201526000907f00000000000000000000000000000000000000000000000000000000000000006001600160a01b03169063bd85b03990602401602060405180830381865afa1580156104d5573d6000803e3d6000fd5b505050506040513d601f19601f8201168201806040525081019061034b9190610ebf565b604051633912022f60e21b81527f000000000000000000000000000000000000000000000000000000000000000060048201526001600160a01b0384811660248301528381166044830152606482018390523360848301526000917f00000000000000000000000000000000000000000000000000000000000000009091169063e44808bc9060a401600060405180830381600087803b15801561059c57600080fd5b505af11580156105b0573d6000803e3d6000fd5b50505050826001600160a01b0316846001600160a01b03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040516105f991815260200190565b60405180910390a35060019392505050565b604051631b2b776160e11b81527f000000000000000000000000000000000000000000000000000000000000000060048201526001600160a01b0382811660248301526000917f000000000000000000000000000000000000000000000000000000000000000090911690633656eec290604401602060405180830381865afa15801561069c573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906104489190610ebf565b604051634e41a1fb60e01b81527f000000000000000000000000000000000000000000000000000000000000000060048201526060907f00000000000000000000000000000000000000000000000000000000000000006001600160a01b031690634e41a1fb90602401610306565b604051633912022f60e21b81527f0000000000000000000000000000000000000000000000000000000000000000600482015233602482018190526001600160a01b0384811660448401526064830184905260848301919091526000917f00000000000000000000000000000000000000000000000000000000000000009091169063e44808bc9060a401600060405180830381600087803b1580156107d457600080fd5b505af11580156107e8573d6000803e3d6000fd5b50506040518481526001600160a01b03861692503391507fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9060200161043c565b8342111561084a5760405163f87d927160e01b815260040160405180910390fd5b6001600160a01b0387166108715760405163f0dd15fd60e01b815260040160405180910390fd5b6001600160a01b038781166000818152602081815260408083205481517f6e71edae12b1b97f4d1f60370fef10105fa2faae0126114a169c64845d6126c98185015280830195909552948b166060850152608084018a905260a0840185905260c08085018a90528151808603909101815260e08501909152805191012061190160f01b6101008401527f0000000000000000000000000000000000000000000000000000000000000000610102840152610122830152906101420160408051601f198184030181528282528051602091820120600080855291840180845281905260ff89169284019290925260608301879052608083018690529092509060019060a0016020604051602081039080840390855afa158015610997573d6000803e3d6000fd5b505050602060405103519050896001600160a01b0316816001600160a01b0316146109d557604051638baa579f60e01b815260040160405180910390fd5b6001600160a01b03808b1660008181526020819052604090819020600187019055516313b4b5ab60e21b81527f000000000000000000000000000000000000000000000000000000000000000060048201528b83166024820152604481018b905260648101919091527f000000000000000000000000000000000000000000000000000000000000000090911690634ed2d6ac90608401600060405180830381600087803b158015610a8657600080fd5b505af1158015610a9a573d6000803e3d6000fd5b50505050886001600160a01b03168a6001600160a01b03167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b9258a604051610ae391815260200190565b60405180910390a350505050505050505050565b60405163e985e9c560e01b81526001600160a01b03838116600483015282811660248301526000917f00000000000000000000000000000000000000000000000000000000000000009091169063e985e9c590604401602060405180830381865afa158015610b6a573d6000803e3d6000fd5b505050506040513d601f19601f82011682018060405250810190610b8e9190610ed8565b15610b9c5750600019610448565b6040516321ff32a960e01b81527f000000000000000000000000000000000000000000000000000000000000000060048201526001600160a01b03848116602483015283811660448301527f000000000000000000000000000000000000000000000000000000000000000016906321ff32a990606401602060405180830381865afa158015610c30573d6000803e3d6000fd5b505050506040513d601f19601f82011682018060405250810190610c549190610ebf565b9050610448565b60005b83811015610c76578181015183820152602001610c5e565b50506000910152565b6020815260008251806020840152610c9e816040850160208701610c5b565b601f01601f19169190910160400192915050565b80356001600160a01b0381168114610cc957600080fd5b919050565b60008060408385031215610ce157600080fd5b610cea83610cb2565b946020939093013593505050565b600080600060608486031215610d0d57600080fd5b610d1684610cb2565b9250610d2460208501610cb2565b9150604084013590509250925092565b600060208284031215610d4657600080fd5b610d4f82610cb2565b9392505050565b600080600080600080600060e0888a031215610d7157600080fd5b610d7a88610cb2565b9650610d8860208901610cb2565b95506040880135945060608801359350608088013560ff81168114610dac57600080fd5b9699959850939692959460a0840135945060c09093013592915050565b60008060408385031215610ddc57600080fd5b610de583610cb2565b9150610df360208401610cb2565b90509250929050565b634e487b7160e01b600052604160045260246000fd5b600060208284031215610e2457600080fd5b815167ffffffffffffffff80821115610e3c57600080fd5b818401915084601f830112610e5057600080fd5b815181811115610e6257610e62610dfc565b604051601f8201601f19908116603f01168101908382118183101715610e8a57610e8a610dfc565b81604052828152876020848701011115610ea357600080fd5b610eb4836020830160208801610c5b565b979650505050505050565b600060208284031215610ed157600080fd5b5051919050565b600060208284031215610eea57600080fd5b81518015158114610d4f57600080fdfea264697066735822122006b63bd07d9695d629a04cdb9e9baf4e33c9c024572b16c142a6ef1434aa554d64736f6c63430008130033a2646970667358221220cedc4e023c4e3e4fe198d6858a28dace1f31cd40657292afc1b716738073186c64736f6c63430008130033"
)


class ForwarderFactoryContract(Contract):
    """A web3.py Contract class for the ForwarderFactory contract."""

    abi: ABI = forwarderfactory_abi
    bytecode: bytes = HexBytes(forwarderfactory_bytecode)

    def __init__(self, address: ChecksumAddress | None = None) -> None:
        try:
            # Initialize parent Contract class
            super().__init__(address=address)
            self.functions = ForwarderFactoryContractFunctions(forwarderfactory_abi, self.w3, address)  # type: ignore

        except FallbackNotFound:
            print("Fallback function not found. Continuing...")

    functions: ForwarderFactoryContractFunctions

    @classmethod
    def constructor(cls) -> ContractConstructor:  # type: ignore
        """Creates a transaction with the contract's constructor function.

        Parameters
        ----------

        w3 : Web3
            A web3 instance.
        account : LocalAccount
            The account to use to deploy the contract.

        Returns
        -------
        Self
            A deployed instance of the contract.

        """

        return super().constructor()

    @classmethod
    def deploy(cls, w3: Web3, account: LocalAccount | ChecksumAddress) -> Self:
        """Deploys and instance of the contract.

        Parameters
        ----------
        w3 : Web3
            A web3 instance.
        account : LocalAccount
            The account to use to deploy the contract.

        Returns
        -------
        Self
            A deployed instance of the contract.
        """
        deployer = cls.factory(w3=w3)
        constructor_fn = deployer.constructor()

        # if an address is supplied, try to use a web3 default account
        if isinstance(account, str):
            tx_hash = constructor_fn.transact({"from": account})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            deployed_contract = deployer(address=tx_receipt.contractAddress)  # type: ignore
            return deployed_contract

        # otherwise use the account provided.
        deployment_tx = constructor_fn.build_transaction()
        current_nonce = w3.eth.get_transaction_count(account.address)
        deployment_tx.update({"nonce": current_nonce})

        # Sign the transaction with local account private key
        signed_tx = account.sign_transaction(deployment_tx)

        # Send the signed transaction and wait for receipt
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        deployed_contract = deployer(address=tx_receipt.contractAddress)  # type: ignore
        return deployed_contract

    @classmethod
    def factory(cls, w3: Web3, class_name: str | None = None, **kwargs: Any) -> Type[Self]:
        """Deploys and instance of the contract.

        Parameters
        ----------
        w3 : Web3
            A web3 instance.
        class_name: str | None
            The instance class name.

        Returns
        -------
        Self
            A deployed instance of the contract.
        """
        contract = super().factory(w3, class_name, **kwargs)
        contract.functions = ForwarderFactoryContractFunctions(forwarderfactory_abi, w3, None)

        return contract
