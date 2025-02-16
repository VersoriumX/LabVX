"""System test for end to end usage of agent0 libraries."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import cast

import pytest
from chainsync.exec import acquire_data, data_analysis
from eth_typing import URI
from ethpy import EthConfig
from ethpy.hyperdrive.addresses import HyperdriveAddresses
from ethpy.hyperdrive.interface import HyperdriveReadInterface
from ethpy.test_fixtures.local_chain import DeployedHyperdrivePool
from fixedpointmath import FixedPoint
from sqlalchemy.orm import Session
from web3 import HTTPProvider

from agent0 import build_account_key_config_from_agent_config
from agent0.base import Trade
from agent0.base.config import AgentConfig, EnvironmentConfig
from agent0.hyperdrive.exec import setup_and_run_agent_loop
from agent0.hyperdrive.policies import HyperdrivePolicy
from agent0.hyperdrive.state import HyperdriveMarketAction, HyperdriveWallet


class WalletTestPolicy(HyperdrivePolicy):
    """An agent that simply cycles through all trades."""

    COUNTER_ADD_LIQUIDITY = 0
    COUNTER_OPEN_LONG = 1
    COUNTER_OPEN_SHORT = 2

    @dataclass(kw_only=True)
    class Config(HyperdrivePolicy.Config):
        """Custom config arguments for this policy.

        Attributes
        ----------
        rerun: bool
            Determines if this policy is being reran
            The second run should be doing assertions for this test
        """

        rerun: bool = False

    # Using default parameters
    def __init__(
        self,
        policy_config: Config,
    ):
        """Initialize config and set counter to 0."""
        # We want to do a sequence of trades one at a time, so we keep an internal counter based on
        # how many times `action` has been called.
        self.counter = 0
        self.rerun = policy_config.rerun
        super().__init__(policy_config)

    def action(
        self, interface: HyperdriveReadInterface, wallet: HyperdriveWallet
    ) -> tuple[list[Trade[HyperdriveMarketAction]], bool]:
        """Open all trades for a fixed amount and closes them after, one at a time.

        Arguments
        ---------
        interface: HyperdriveReadInterface
            The trading market interface.
        wallet: HyperdriveWallet
            The agent's wallet.

        Returns
        -------
        tuple[list[HyperdriveMarketAction], bool]
            A tuple where the first element is a list of actions,
            and the second element defines if the agent is done trading
        """
        # pylint: disable=unused-argument
        action_list = []
        done_trading = False

        if self.rerun:
            # assert wallet state was loaded from previous run
            assert len(wallet.longs) == 1
            assert len(wallet.shorts) == 1
            # TODO would like to check long and lp value here,
            # but the units there are in bonds and lp shares respectively,
            # where the known value of the trade is in units of base.
            assert wallet.shorts[list(wallet.shorts.keys())[0]].balance == FixedPoint(33_333)

            # We want this bot to exit and crash after it's done the trades it needs to do
            done_trading = True

        if self.counter == self.COUNTER_ADD_LIQUIDITY:
            # Add liquidity
            action_list.append(interface.add_liquidity_trade(trade_amount=FixedPoint(111_111)))
        elif self.counter == self.COUNTER_OPEN_LONG:
            # Open Long
            action_list.append(interface.open_long_trade(FixedPoint(22_222)))
        elif self.counter == self.COUNTER_OPEN_SHORT:
            # Open Short
            action_list.append(interface.open_short_trade(FixedPoint(33_333)))
        else:
            done_trading = True
        self.counter += 1
        return action_list, done_trading


class TestBotToDb:
    """Test pipeline from bots making trades to viewing the trades in the db."""

    # TODO split this up into different functions that work with tests
    # pylint: disable=too-many-locals, too-many-statements
    @pytest.mark.anvil
    def test_bot_to_db(
        self,
        local_hyperdrive_pool: DeployedHyperdrivePool,
        db_session: Session,
        db_api: str,
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
                policy=WalletTestPolicy,
                number_of_agents=1,
                base_budget_wei=FixedPoint("1_000_000").scaled_value,  # 1 million base
                eth_budget_wei=FixedPoint("100").scaled_value,  # 100 base
                policy_config=WalletTestPolicy.Config(
                    slippage_tolerance=FixedPoint("0.0001"),
                    rerun=False,
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
            database_api_uri=db_api,
            # Using default abi dir
        )

        setup_and_run_agent_loop(
            env_config,
            agent_config,
            account_key_config,
            eth_config=eth_config,
            contract_addresses=hyperdrive_contract_addresses,
        )

        # Run acquire data to get data from chain to db
        acquire_data(
            start_block=local_hyperdrive_pool.deploy_block_number,  # We only want to get data past the deploy block
            eth_config=eth_config,
            db_session=db_session,
            contract_addresses=hyperdrive_contract_addresses,
            # Exit the script after catching up to the chain
            exit_on_catch_up=True,
        )

        # Run data analysis to calculate various analysis values
        data_analysis(
            start_block=local_hyperdrive_pool.deploy_block_number,  # We only want to get data past the deploy block
            eth_config=eth_config,
            db_session=db_session,
            contract_addresses=hyperdrive_contract_addresses,
            # Exit the script after catching up to the chain
            exit_on_catch_up=True,
        )

        # Run bots again, this time ensuring wallet is up to date

        # Build agent config
        agent_config: list[AgentConfig] = [
            AgentConfig(
                policy=WalletTestPolicy,
                number_of_agents=1,
                base_budget_wei=FixedPoint("1_000_000").scaled_value,  # 1 million base
                eth_budget_wei=FixedPoint("100").scaled_value,  # 100 base
                policy_config=WalletTestPolicy.Config(
                    slippage_tolerance=FixedPoint("0.0001"),
                    rerun=False,
                ),
            ),
        ]

        setup_and_run_agent_loop(
            env_config,
            agent_config,
            account_key_config,
            eth_config=eth_config,
            contract_addresses=hyperdrive_contract_addresses,
        )
