"""Fuzz test to verify that if all of the funds are removed from Hyperdrive, there is no base left in the contract."""
# %%
# Imports
from __future__ import annotations

import json
import logging
from dataclasses import asdict

import numpy as np
from fixedpointmath import FixedPoint
from hyperlogs import ExtendedJSONEncoder, setup_logging

from agent0.hyperdrive.interactive import InteractiveHyperdrive, LocalChain
from agent0.hyperdrive.interactive.event_types import OpenLong, OpenShort
from agent0.hyperdrive.interactive.interactive_hyperdrive_agent import InteractiveHyperdriveAgent
from agent0.hyperdrive.state.hyperdrive_actions import HyperdriveActionType

# Variables by themselves print out dataframes in a nice format in interactive mode
# pylint: disable=pointless-statement
# pylint: disable=invalid-name

# %%
# Set global defaults
NUM_TRADES = 3
FAILED = False

# %%
# Setup logging
log_filename = ".logging/fuzz_hyperdrive_balance.log"
setup_logging(
    log_filename=log_filename,
    delete_previous_logs=True,
    log_stdout=False,
)
# %%
# Setup local chain
chain_config = LocalChain.Config()
chain = LocalChain(config=chain_config)
random_seed = np.random.randint(low=1, high=99999999)  # No seed, we want this to be random every time it is executed
rng = np.random.default_rng(random_seed)

# %%
# Parameters for pool initialization.
initial_pool_config = InteractiveHyperdrive.Config(preview_before_trade=True)
interactive_hyperdrive = InteractiveHyperdrive(chain, initial_pool_config)

# %%

# Get initial vault shares
pool_state = interactive_hyperdrive.hyperdrive_interface.get_hyperdrive_state()
initial_vault_shares = pool_state.vault_shares


# %%
# Generate a list of agents that execute random trades
available_actions = np.array([HyperdriveActionType.OPEN_LONG, HyperdriveActionType.OPEN_SHORT])
min_trade = interactive_hyperdrive.hyperdrive_interface.pool_config.minimum_transaction_amount
trade_list: list[tuple[InteractiveHyperdriveAgent, HyperdriveActionType, FixedPoint]] = []
for agent_index in range(NUM_TRADES):  # 1 agent per trade
    budget = FixedPoint(
        scaled_value=int(np.floor(rng.uniform(low=min_trade.scaled_value * 10, high=int(1e23))))
    )  # Give a little extra money to account for fees
    agent = interactive_hyperdrive.init_agent(base=budget, eth=FixedPoint(100))
    trade_type = rng.choice(available_actions, size=1)[0]
    trade_amount_base = FixedPoint(
        scaled_value=int(
            rng.uniform(
                low=min_trade.scaled_value,
                high=int(
                    budget.scaled_value / 2
                ),  # Don't trade all of their money, to make sure they have enough for fees
            )
        )
    )
    trade_list.append((agent, trade_type, trade_amount_base))


# %%
# Open some trades
trade_events: list[tuple[InteractiveHyperdriveAgent, OpenLong | OpenShort]] = []
for trade in trade_list:
    agent, trade_type, trade_amount = trade
    if trade_type == HyperdriveActionType.OPEN_LONG:
        trade_event = agent.open_long(base=trade_amount)
    elif trade_type == HyperdriveActionType.OPEN_SHORT:
        trade_event = agent.open_short(bonds=trade_amount)
    else:
        raise AssertionError(f"{trade_type=} is not supported.")
    trade_events.append((agent, trade_event))

# %%
# Advance some time
chain.advance_time(
    rng.integers(low=0, high=interactive_hyperdrive.hyperdrive_interface.pool_config.position_duration - 1),
    create_checkpoints=True,
)

# %%
# Close the trades
for agent, trade in trade_events:
    if isinstance(trade, OpenLong):
        agent.close_long(maturity_time=trade.maturity_time, bonds=trade.bond_amount)
    if isinstance(trade, OpenShort):
        agent.close_short(maturity_time=trade.maturity_time, bonds=trade.bond_amount)

# %%
# Check the reserve amounts; they should be unchanged now that all of the trades are closed
pool_state = interactive_hyperdrive.hyperdrive_interface.get_hyperdrive_state()
if pool_state.vault_shares != initial_vault_shares:
    logging.critical("vault_shares=%s != initial_vault_shares=%s", pool_state.vault_shares, initial_vault_shares)
    FAILED = True
if pool_state.pool_info.share_reserves < pool_state.pool_config.minimum_share_reserves:
    logging.critical(
        "share_reserves=%s < minimum_share_reserves=%s",
        pool_state.pool_info.share_reserves,
        pool_state.pool_config.minimum_share_reserves,
    )
    FAILED = True

if FAILED:
    logging.info(
        "random_seed = %s\npool_config = %s\n\npool_info = %s\n\nlatest_checkpoint = %s\n\nadditional_info = %s",
        random_seed,
        json.dumps(asdict(pool_state.pool_config), indent=2, cls=ExtendedJSONEncoder),
        json.dumps(asdict(pool_state.pool_info), indent=2, cls=ExtendedJSONEncoder),
        json.dumps(asdict(pool_state.checkpoint), indent=2, cls=ExtendedJSONEncoder),
        json.dumps(
            {
                "hyperdrive_address": interactive_hyperdrive.hyperdrive_interface.hyperdrive_contract.address,
                "base_token_address": interactive_hyperdrive.hyperdrive_interface.base_token_contract.address,
                "spot_price": interactive_hyperdrive.hyperdrive_interface.calc_spot_price(pool_state),
                "fixed_rate": interactive_hyperdrive.hyperdrive_interface.calc_fixed_rate(pool_state),
                "variable_rate": pool_state.variable_rate,
                "vault_shares": pool_state.vault_shares,
            },
            indent=2,
            cls=ExtendedJSONEncoder,
        ),
    )
    raise AssertionError(f"Testing failed; see logs in {log_filename}")
