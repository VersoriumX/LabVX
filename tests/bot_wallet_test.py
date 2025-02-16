"""System test for checking calculated wallets versus wallets on chain."""
from __future__ import annotations

import logging
import os
from typing import cast

import pytest
from eth_typing import URI
from ethpy import EthConfig
from ethpy.hyperdrive import AssetIdPrefix, encode_asset_id
from ethpy.hyperdrive.addresses import HyperdriveAddresses
from ethpy.hyperdrive.interface import HyperdriveReadInterface
from ethpy.test_fixtures.local_chain import DeployedHyperdrivePool
from fixedpointmath import FixedPoint
from web3 import HTTPProvider

from agent0 import build_account_key_config_from_agent_config
from agent0.base import Trade
from agent0.base.config import AgentConfig, EnvironmentConfig
from agent0.hyperdrive.exec import setup_and_run_agent_loop
from agent0.hyperdrive.policies import HyperdrivePolicy
from agent0.hyperdrive.state import HyperdriveMarketAction, HyperdriveWallet


def ensure_agent_wallet_is_correct(wallet: HyperdriveWallet, interface: HyperdriveReadInterface) -> None:
    """Check that the agent's wallet matches what's reported from the chain.

    Will assert that balances match.

    Arguments
    ---------
    wallet: HyperdriveWallet
        The HyperdriveWallet object to check against the chain
    interface: HyperdriveReadInterface
        The Hyperdrive API interface object
    """
    # Check base
    base_from_chain = interface.base_token_contract.functions.balanceOf(
        interface.web3.to_checksum_address(wallet.address.hex())
    ).call()
    assert wallet.balance.amount == FixedPoint(scaled_value=base_from_chain)

    # Check lp positions
    asset_id = encode_asset_id(AssetIdPrefix.LP, 0)
    address = interface.web3.to_checksum_address(wallet.address.hex())
    lp_from_chain = interface.hyperdrive_contract.functions.balanceOf(asset_id, address).call()
    assert wallet.lp_tokens == FixedPoint(scaled_value=lp_from_chain)

    # Check withdrawal positions
    asset_id = encode_asset_id(AssetIdPrefix.WITHDRAWAL_SHARE, 0)
    address = interface.web3.to_checksum_address(wallet.address.hex())
    withdrawal_from_chain = interface.hyperdrive_contract.functions.balanceOf(asset_id, address).call()
    assert wallet.withdraw_shares == FixedPoint(scaled_value=withdrawal_from_chain)

    # Check long positions
    for long_time, long_amount in wallet.longs.items():
        asset_id = encode_asset_id(AssetIdPrefix.LONG, long_time)
        address = interface.web3.to_checksum_address(wallet.address.hex())
        long_from_chain = interface.hyperdrive_contract.functions.balanceOf(asset_id, address).call()
        assert long_amount.balance == FixedPoint(scaled_value=long_from_chain)

    # Check short positions
    for short_time, short_amount in wallet.shorts.items():
        asset_id = encode_asset_id(AssetIdPrefix.SHORT, short_time)
        address = interface.web3.to_checksum_address(wallet.address.hex())
        short_from_chain = interface.hyperdrive_contract.functions.balanceOf(asset_id, address).call()
        assert short_amount.balance == FixedPoint(scaled_value=short_from_chain)


class WalletTestAgainstChainPolicy(HyperdrivePolicy):
    """An agent that simply cycles through all trades."""

    COUNTER_ADD_LIQUIDITY = 0
    COUNTER_OPEN_LONG = 1
    COUNTER_OPEN_SHORT = 2
    COUNTER_REMOVE_LIQUIDITY = 3
    COUNTER_CLOSE_LONGS = 4
    COUNTER_CLOSE_SHORTS = 5
    COUNTER_REDEEM_WITHDRAW_SHARES = 6
    COUNTER_CHECK = 7

    counter = 0

    def action(
        self, interface: HyperdriveReadInterface, wallet: HyperdriveWallet
    ) -> tuple[list[Trade[HyperdriveMarketAction]], bool]:
        """Open all trades for a fixed amount and closes them after, one at a time.

        After each trade, the agent will ensure the wallet passed in matches what's on the chain.

        Arguments
        ---------
        interface: HyperdriveReadInterface
            The trading market.
        wallet: HyperdriveWallet
            agent's wallet

        Returns
        -------
        tuple[list[MarketAction], bool]
            A tuple where the first element is a list of actions,
            and the second element defines if the agent is done trading
        """
        # pylint: disable=unused-argument
        action_list = []
        done_trading = False

        if self.counter == self.COUNTER_ADD_LIQUIDITY:
            # Add liquidity
            action_list.append(interface.add_liquidity_trade(trade_amount=FixedPoint(111_111)))
        elif self.counter == self.COUNTER_OPEN_LONG:
            # Open Long
            action_list.append(interface.open_long_trade(FixedPoint(22_222), self.slippage_tolerance))
        elif self.counter == self.COUNTER_OPEN_SHORT:
            # Open Short
            action_list.append(interface.open_short_trade(FixedPoint(333), self.slippage_tolerance))
        elif self.counter == self.COUNTER_REMOVE_LIQUIDITY:
            # Remove All Liquidity
            action_list.append(interface.remove_liquidity_trade(wallet.lp_tokens))
        elif self.counter == self.COUNTER_CLOSE_LONGS:
            # Close All Longs
            assert len(wallet.longs) == 1
            for long_time, long in wallet.longs.items():
                action_list.append(interface.close_long_trade(long.balance, long_time, self.slippage_tolerance))
        elif self.counter == self.COUNTER_CLOSE_SHORTS:
            # Close All Shorts
            assert len(wallet.shorts) == 1
            for short_time, short in wallet.shorts.items():
                action_list.append(interface.close_short_trade(short.balance, short_time, self.slippage_tolerance))
        elif self.counter == self.COUNTER_REDEEM_WITHDRAW_SHARES:
            # Redeem all withdrawal shares
            action_list.append(interface.redeem_withdraw_shares_trade(wallet.withdraw_shares))
        elif self.counter == self.COUNTER_CHECK:
            # One final check after the previous trade
            pass
        else:
            done_trading = True

        # After each trade, check the wallet for correctness against the chain
        ensure_agent_wallet_is_correct(wallet, interface)
        self.counter += 1
        return action_list, done_trading


class TestWalletAgainstChain:
    """Test pipeline from bots making trades to viewing the trades in the db."""

    # TODO split this up into different functions that work with tests
    # pylint: disable=too-many-locals, too-many-statements
    @pytest.mark.anvil
    def test_wallet_against_chain(
        self,
        local_hyperdrive_pool: DeployedHyperdrivePool,
    ):
        """Runs the entire pipeline and checks the database at the end. All arguments are fixtures."""
        # Run this test with develop mode on
        os.environ["DEVELOP"] = "true"

        # Get hyperdrive chain info
        uri: URI | None = cast(HTTPProvider, local_hyperdrive_pool.web3.provider).endpoint_uri
        rpc_uri = uri if uri else URI("http://localhost:8545")
        hyperdrive_contract_addresses: HyperdriveAddresses = local_hyperdrive_pool.hyperdrive_contract_addresses

        # Build environment config
        env_config = EnvironmentConfig(
            delete_previous_logs=False,
            halt_on_errors=True,
            log_filename="system_test",
            log_level=logging.INFO,
            log_stdout=True,
            global_random_seed=1234,
            username="test",
        )

        # Build agent config
        agent_config: list[AgentConfig] = [
            AgentConfig(
                policy=WalletTestAgainstChainPolicy,
                number_of_agents=1,
                base_budget_wei=FixedPoint("10_000_000").scaled_value,  # 10 million base
                eth_budget_wei=FixedPoint("100").scaled_value,  # 100 base
                policy_config=WalletTestAgainstChainPolicy.Config(
                    slippage_tolerance=FixedPoint("0.0001"),
                ),
            ),
        ]

        # No need for random seed, this bot is deterministic
        account_key_config = build_account_key_config_from_agent_config(agent_config)

        # Build custom eth config pointing to local test chain
        eth_config = EthConfig(
            # Artifacts_uri isn't used here, as we explicitly set addresses and passed to run_bots
            artifacts_uri="not_used",
            rpc_uri=rpc_uri,
            database_api_uri="not_used",
            # Using default abi dir
        )

        setup_and_run_agent_loop(
            env_config,
            agent_config,
            account_key_config,
            eth_config=eth_config,
            contract_addresses=hyperdrive_contract_addresses,
            load_wallet_state=False,
        )
