"""Script to verify that longs and shorts which are closed at maturity supply the correct amounts."""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, NamedTuple, Sequence

import numpy as np
from fixedpointmath import FixedPoint
from hypertypes.fixedpoint_types import CheckpointFP

from agent0.hyperdrive.crash_report import build_crash_trade_result, log_hyperdrive_crash_report
from agent0.hyperdrive.interactive import InteractiveHyperdrive, LocalChain
from agent0.hyperdrive.interactive.event_types import CloseLong, CloseShort, OpenLong, OpenShort
from agent0.interactive_fuzz.helpers import FuzzAssertionException, generate_trade_list, open_random_trades, setup_fuzz

# main script has a lot of stuff going on
# pylint: disable=too-many-locals


def main(argv: Sequence[str] | None = None):
    """Primary entrypoint.

    Arguments
    ---------
    argv: Sequence[str]
        The argv values returned from argparser.
    """
    # Setup the experiment
    parsed_args = parse_arguments(argv)
    fuzz_long_short_maturity_values(*parsed_args)


def fuzz_long_short_maturity_values(
    num_trades: int, chain_config: LocalChain.Config | None = None, log_to_stdout: bool = False
):
    """Does fuzzy invariant checks on closing longs and shorts past maturity.

    Parameters
    ----------
    num_trades: int
        Number of trades to perform during the fuzz tests.
    chain_config: LocalChain.Config, optional
        Configuration options for the local chain.
    log_to_stdout: bool, optional
        If True, log to stdout in addition to a file.
        Defaults to False.
    """

    log_filename = ".logging/fuzz_long_short_maturity_values.log"
    # Parameters for local chain initialization, defines defaults in constructor
    # set a large block time so i can manually control when it ticks
    # TODO: set block time really high after contracts deployed:
    # chain_config = LocalChain.Config(block_time=1_000_000)
    chain, random_seed, rng, interactive_hyperdrive = setup_fuzz(log_filename, chain_config, log_to_stdout)
    signer = interactive_hyperdrive.init_agent(eth=FixedPoint(100))

    # Advance time to ensure current time is in the middle of a checkpoint
    current_block_time = interactive_hyperdrive.hyperdrive_interface.get_block_timestamp(
        interactive_hyperdrive.hyperdrive_interface.get_current_block()
    )
    time_to_next_checkpoint = (
        current_block_time % interactive_hyperdrive.hyperdrive_interface.pool_config.checkpoint_duration
    )
    # Add a small amount to ensure we're not at the edge of a checkpoint
    # This prevents the latter step of `chain.advance_time(position_duration+30)` advancing past a checkpoint
    # Also prevents `open_random_trades` from passing the create checkpoint barrier
    logging.info("Advance time...")
    chain.advance_time(time_to_next_checkpoint + 100, create_checkpoints=True)

    # Generate a list of agents that execute random trades
    trade_list = generate_trade_list(num_trades, rng, interactive_hyperdrive)

    # Open some trades
    logging.info("Open random trades...")
    trade_events = open_random_trades(trade_list, chain, rng, interactive_hyperdrive, advance_time=False)

    # Ensure all trades open are within the same checkpoint
    trade_maturity_times = []
    for agent, event in trade_events:
        trade_maturity_times.append(event.maturity_time)
    assert all(maturity_time == trade_maturity_times[0] for maturity_time in trade_maturity_times)

    # Starting checkpoint is automatically created by sending transactions
    starting_checkpoint = interactive_hyperdrive.hyperdrive_interface.current_pool_state.checkpoint

    # Advance the time to a little more than the position duration
    logging.info("Advance time...")
    position_duration = interactive_hyperdrive.hyperdrive_interface.pool_config.position_duration
    chain.advance_time(position_duration + 30, create_checkpoints=False)

    # Create a checkpoint
    logging.info("Create a checkpoint...")
    # Get the maturity checkpoint for the previously created checkpoint
    checkpoint_id = interactive_hyperdrive.hyperdrive_interface.calc_checkpoint_id()
    interactive_hyperdrive.hyperdrive_interface.create_checkpoint(signer.agent, checkpoint_time=checkpoint_id)
    maturity_checkpoint = interactive_hyperdrive.hyperdrive_interface.current_pool_state.checkpoint

    # TODO ensure this maturity checkpoint is the maturity of all open positions
    for trade_maturity_time in trade_maturity_times:
        assert checkpoint_id == trade_maturity_time

    # Advance time again
    logging.info("Advance time...")
    extra_time = int(np.floor(rng.uniform(low=0, high=position_duration)))
    chain.advance_time(extra_time, create_checkpoints=False)

    # Close the trades one at a time, check invariants
    for index, (agent, trade) in enumerate(trade_events):
        logging.info("closing trade %s out of %s\n", index, len(trade_events) - 1)
        if isinstance(trade, OpenLong):
            close_event = agent.close_long(maturity_time=trade.maturity_time, bonds=trade.bond_amount)
        elif isinstance(trade, OpenShort):
            close_event = agent.close_short(maturity_time=trade.maturity_time, bonds=trade.bond_amount)
        else:
            assert False

        try:
            invariant_check(trade, close_event, starting_checkpoint, maturity_checkpoint, interactive_hyperdrive)
        except FuzzAssertionException as error:
            dump_state_dir = chain.save_state(save_prefix="fuzz_long_short_maturity_values")
            additional_info = {"fuzz_random_seed": random_seed, "dump_state_dir": dump_state_dir}
            additional_info.update(error.exception_data)
            report = build_crash_trade_result(
                error, interactive_hyperdrive.hyperdrive_interface, agent.agent, additional_info=additional_info
            )
            # Crash reporting already going to file in logging
            log_hyperdrive_crash_report(
                report,
                crash_report_to_file=True,
                crash_report_file_prefix="fuzz_long_short_maturity_values",
                log_to_rollbar=True,
            )
            chain.cleanup()
            raise error

    chain.cleanup()
    logging.info("Test passed!")


class Args(NamedTuple):
    """Command line arguments for the invariant checker."""

    num_trades: int
    chain_config: LocalChain.Config
    log_to_stdout: bool


def namespace_to_args(namespace: argparse.Namespace) -> Args:
    """Converts argprase.Namespace to Args.

    Arguments
    ---------
    namespace: argparse.Namespace
        Object for storing arg attributes.

    Returns
    -------
    Args
        Formatted arguments
    """
    # TODO: replace this func with Args(**namespace)?
    return Args(
        num_trades=namespace.num_trades,
        chain_config=LocalChain.Config(chain_port=namespace.chain_port),
        log_to_stdout=namespace.log_to_stdout,
    )


def parse_arguments(argv: Sequence[str] | None = None) -> Args:
    """Parses input arguments.

    Arguments
    ---------
    argv: Sequence[str]
        The argv values returned from argparser.

    Returns
    -------
    Args
        Formatted arguments
    """
    parser = argparse.ArgumentParser(description="Runs a loop to check Hyperdrive invariants at each block.")
    parser.add_argument(
        "--num_trades",
        type=int,
        default=5,
        help="The number of random trades to open.",
    )
    parser.add_argument(
        "--chain_port",
        type=int,
        default=10000,
        help="The number of random trades to open.",
    )
    parser.add_argument(
        "--log_to_stdout",
        type=bool,
        default=False,
        help="If True, log to stdout in addition to a file.",
    )
    # Use system arguments if none were passed
    if argv is None:
        argv = sys.argv
    return namespace_to_args(parser.parse_args())


# pylint: disable=too-many-arguments
def invariant_check(
    open_trade_event: OpenLong | OpenShort,
    close_trade_event: CloseLong | CloseShort,
    starting_checkpoint: CheckpointFP,
    maturity_checkpoint: CheckpointFP,
    interactive_hyperdrive: InteractiveHyperdrive,
) -> None:
    """Check the pool state invariants and throws an assertion exception if fails.

    Arguments
    ---------
    open_trade_event: OpenLong | OpenShort
        The OpenLong or OpenShort event that resulted from opening the position.
    close_trade_event: CloseLong | CloseShort
        The CloseLong or CloseShort event that resulted from closing the position.
    starting_checkpoint: CheckpointFP
        The starting checkpoint.
    maturity_checkpoint: CheckpointFP
        The maturity checkpoint.
    interactive_hyperdrive: InteractiveHyperdrive
        An instantiated InteractiveHyperdrive object.
    """
    failed = False

    exception_message: list[str] = ["Fuzz Long/Short Maturity Values Invariant Check"]
    exception_data: dict[str, Any] = {}

    if isinstance(open_trade_event, OpenLong) and isinstance(close_trade_event, CloseLong):
        # 0.05 would be a 5% fee.
        flat_fee_percent = interactive_hyperdrive.hyperdrive_interface.pool_config.fees.flat

        # assert with trade values
        # base out should be equal to bonds in minus the flat fee.
        actual_base_amount = close_trade_event.base_amount
        expected_base_amount_from_event = (
            close_trade_event.bond_amount - close_trade_event.bond_amount * flat_fee_percent
        )

        # assert with event values
        if actual_base_amount != expected_base_amount_from_event:
            difference_in_wei = abs(actual_base_amount.scaled_value - expected_base_amount_from_event.scaled_value)
            exception_message.append(
                f"{actual_base_amount=} != {expected_base_amount_from_event=}, {difference_in_wei=}"
            )
            exception_data["invariance_check:actual_base_amount"] = actual_base_amount
            exception_data["invariance_check:expected_base_amount_from_event"] = expected_base_amount_from_event
            exception_data["invariance_check:base_amount_from_event_difference_in_wei"] = difference_in_wei
            failed = True

        expected_base_amount_from_trade = open_trade_event.bond_amount - open_trade_event.bond_amount * flat_fee_percent
        if actual_base_amount != expected_base_amount_from_trade:
            difference_in_wei = abs(actual_base_amount.scaled_value - expected_base_amount_from_trade.scaled_value)
            exception_message.append(
                f"{actual_base_amount=} != {expected_base_amount_from_trade=}, {difference_in_wei=}"
            )
            exception_data["invariance_check:actual_base_amount"] = actual_base_amount
            exception_data["invariance_check:expected_base_amount_from_trade"] = expected_base_amount_from_trade
            exception_data["invariance_check:base_amount_from_trade_difference_in_wei"] = difference_in_wei
            failed = True

    elif isinstance(open_trade_event, OpenShort) and isinstance(close_trade_event, CloseShort):
        # get the share prices
        open_share_price = starting_checkpoint.share_price
        closing_share_price = maturity_checkpoint.share_price

        # interested accrued in shares = (c1 / c0 + flat_fee) * dy - c1 * dz
        flat_fee_percent = interactive_hyperdrive.hyperdrive_interface.pool_config.fees.flat

        # get the share amount, c1 * dz part of the equation.
        share_reserves_delta = open_trade_event.bond_amount
        flat_fee = open_trade_event.bond_amount * flat_fee_percent
        share_reserves_delta_plus_flat_fee = share_reserves_delta + flat_fee

        # get the final interest accrued
        interest_accrued = (
            open_trade_event.bond_amount * (closing_share_price / open_share_price + flat_fee_percent)
            - share_reserves_delta_plus_flat_fee
        )

        actual_base_amount = close_trade_event.base_amount
        if actual_base_amount != interest_accrued:
            difference_in_wei = abs(actual_base_amount.scaled_value - interest_accrued.scaled_value)
            exception_message.append(f"{actual_base_amount=} != {interest_accrued=}, {difference_in_wei=}")
            exception_data["invariance_check:actual_base_amount"] = actual_base_amount
            exception_data["invariance_check:interest_accured"] = interest_accrued
            exception_data["invariance_check:short_base_amount_difference_in_wei"] = difference_in_wei
            failed = True
    else:
        raise ValueError("Invalid types for open/close trade events")

    if failed:
        logging.critical("\n".join(exception_message))
        raise FuzzAssertionException(*exception_message, exception_data=exception_data)


if __name__ == "__main__":
    main()
