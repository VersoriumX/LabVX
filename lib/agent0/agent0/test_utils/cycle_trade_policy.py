"""Pytest fixture that creates an in memory db session and creates dummy db schemas"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Type

import pytest
from ethpy.hyperdrive.interface import HyperdriveReadInterface
from fixedpointmath import FixedPoint

from agent0.base import MarketType, Trade
from agent0.hyperdrive.policies import HyperdrivePolicy
from agent0.hyperdrive.state import HyperdriveActionType, HyperdriveMarketAction, HyperdriveWallet


# Build custom policy
# Simple agent, opens a set of all trades for a fixed amount and closes them after
class CycleTradesPolicy(HyperdrivePolicy):
    """A agent that simply cycles through all trades"""

    @dataclass(kw_only=True)
    class Config(HyperdrivePolicy.Config):
        """Custom config arguments for this policy

        Attributes
        ----------
        max_trades: int
            The maximum amount of trades to make before this policy is done trading
        """

        max_trades: int | None = None

    # Using default parameters
    def __init__(
        self,
        policy_config: Config,
    ):
        # We want to do a sequence of trades one at a time, so we keep an internal counter based on
        # how many times `action` has been called.
        self.counter = 0
        self.max_trades = policy_config.max_trades
        super().__init__(policy_config)

    def action(
        self, interface: HyperdriveReadInterface, wallet: HyperdriveWallet
    ) -> tuple[list[Trade[HyperdriveMarketAction]], bool]:
        """This agent simply opens all trades for a fixed amount and closes them after, one at a time

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

        # Early stopping based on parameter
        if (self.max_trades is not None) and (self.counter >= self.max_trades):
            # We want this bot to exit and crash after it's done the trades it needs to do
            return [], True

        if self.counter == 0:
            # Add liquidity
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.ADD_LIQUIDITY,
                        trade_amount=FixedPoint(11111),
                        wallet=wallet,
                    ),
                )
            )
        elif self.counter == 1:
            # Open Long
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.OPEN_LONG,
                        trade_amount=FixedPoint(22222),
                        slippage_tolerance=self.slippage_tolerance,
                        wallet=wallet,
                    ),
                )
            )
        elif self.counter == 2:
            # Open Short
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.OPEN_SHORT,
                        trade_amount=FixedPoint(33333),
                        slippage_tolerance=self.slippage_tolerance,
                        wallet=wallet,
                    ),
                )
            )
        elif self.counter == 3:
            # Remove All Liquidity
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.REMOVE_LIQUIDITY,
                        trade_amount=wallet.lp_tokens,
                        wallet=wallet,
                    ),
                )
            )
        elif self.counter == 4:
            # Close All Longs
            assert len(wallet.longs) == 1
            for long_time, long in wallet.longs.items():
                action_list.append(
                    Trade(
                        market_type=MarketType.HYPERDRIVE,
                        market_action=HyperdriveMarketAction(
                            action_type=HyperdriveActionType.CLOSE_LONG,
                            trade_amount=long.balance,
                            slippage_tolerance=self.slippage_tolerance,
                            wallet=wallet,
                            maturity_time=long_time,
                        ),
                    )
                )
        elif self.counter == 5:
            # Close All Shorts
            assert len(wallet.shorts) == 1
            for short_time, short in wallet.shorts.items():
                action_list.append(
                    Trade(
                        market_type=MarketType.HYPERDRIVE,
                        market_action=HyperdriveMarketAction(
                            action_type=HyperdriveActionType.CLOSE_SHORT,
                            trade_amount=short.balance,
                            slippage_tolerance=self.slippage_tolerance,
                            wallet=wallet,
                            # TODO is this actually maturity time? Not mint time?
                            maturity_time=short_time,
                        ),
                    )
                )
        elif self.counter == 6:
            # Redeem all withdrawal shares
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.REDEEM_WITHDRAW_SHARE,
                        trade_amount=wallet.withdraw_shares,
                        wallet=wallet,
                    ),
                )
            )
        else:
            done_trading = True
        self.counter += 1
        return action_list, done_trading


@pytest.fixture(scope="function")
def cycle_trade_policy() -> Type[CycleTradesPolicy]:
    """Test fixture to build a policy that cycles through all trades.

    Returns
    -------
    CycleTradesPolicy
        A policy that cycles through all trades.
    """
    return CycleTradesPolicy
