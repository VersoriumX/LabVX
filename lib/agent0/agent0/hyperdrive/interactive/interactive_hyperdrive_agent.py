"""The hyperdrive agent object that encapsulates an agent."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type

    from fixedpointmath import FixedPoint

    from agent0.hyperdrive.policies import HyperdrivePolicy
    from agent0.hyperdrive.state import HyperdriveWallet

    from .event_types import (
        AddLiquidity,
        CloseLong,
        CloseShort,
        OpenLong,
        OpenShort,
        RedeemWithdrawalShares,
        RemoveLiquidity,
    )
    from .interactive_hyperdrive import InteractiveHyperdrive


# We keep this class bare bones, while we want the logic functions in InteractiveHyperdrive to be private
# Hence, we call protected class methods in this class.
# pylint: disable=protected-access


class InteractiveHyperdriveAgent:
    """Interactive Hyperdrive Agent.
    This class is barebones with documentation, will just call the corresponding function
    in the interactive hyperdrive class to keep all logic in the same place. Adding these
    wrappers here for ease of use.
    """

    def __init__(
        self,
        base: FixedPoint,
        eth: FixedPoint,
        name: str | None,
        pool: InteractiveHyperdrive,
        policy: Type[HyperdrivePolicy] | None,
        policy_config: HyperdrivePolicy.Config | None,
        private_key: str | None = None,
    ) -> None:
        """Constructor for the interactive hyperdrive agent.
        NOTE: this constructor shouldn't be called directly, but rather from InteractiveHyperdrive's
        `init_agent` method.

        Arguments
        ---------
        base: FixedPoint
            The amount of base to fund the agent with.
        eth: FixedPoint
            The amount of ETH to fund the agent with.
        name: str | None
            The name of the agent. Defaults to the wallet address.
        pool: InteractiveHyperdrive
            The pool object that this agent belongs to.
        policy: HyperdrivePolicy | None
            An optional policy to attach to this agent.
        private_key: str | None, optional
            The private key of the associated account. Default is auto-generated.
        """
        # pylint: disable=too-many-arguments
        self._pool = pool
        self.name = name
        self.agent = self._pool._init_agent(base, eth, name, policy, policy_config, private_key)

    @property
    def wallet(self) -> HyperdriveWallet:
        """Returns the agent's current wallet.

        Returns
        -------
        HyperdriveWallet
            The agent's current wallet.
        """
        return self.agent.wallet

    def add_funds(self, base: FixedPoint | None = None, eth: FixedPoint | None = None) -> None:
        """Adds additional funds to the agent.

        Arguments
        ---------
        base: FixedPoint
            The amount of base to fund the agent with. Defaults to 0.
        eth: FixedPoint
            The amount of ETH to fund the agent with. Defaults to 0.
        """
        if base is None:
            base = FixedPoint(0)
        if eth is None:
            eth = FixedPoint(0)
        self._pool._add_funds(self.agent, base, eth)

    def open_long(self, base: FixedPoint) -> OpenLong:
        """Opens a long for this agent.

        Arguments
        ---------
        base: FixedPoint
            The amount of longs to open in units of base.

        Returns
        -------
        OpenLong
            The emitted event of the open long call.
        """
        return self._pool._open_long(self.agent, base)

    def close_long(self, maturity_time: int, bonds: FixedPoint) -> CloseLong:
        """Closes a long for this agent.

        Arguments
        ---------
        maturity_time: int
            The maturity time of the bonds to close. This is the identifier of the long tokens.
        bonds: FixedPoint
            The amount of longs to close in units of bonds.

        Returns
        -------
        CloseLong
            The emitted event of the close long call.
        """
        return self._pool._close_long(self.agent, maturity_time, bonds)

    def open_short(self, bonds: FixedPoint) -> OpenShort:
        """Opens a short for this agent.

        Arguments
        ---------
        bonds: FixedPoint
            The amount of shorts to open in units of bonds.

        Returns
        -------
        OpenShort
            The emitted event of the open short call.
        """
        return self._pool._open_short(self.agent, bonds)

    def close_short(self, maturity_time: int, bonds: FixedPoint) -> CloseShort:
        """Closes a short for this agent.

        Arguments
        ---------
        maturity_time: int
            The maturity time of the bonds to close. This is the identifier of the short tokens.
        bonds: FixedPoint
            The amount of shorts to close in units of bonds.

        Returns
        -------
        CloseShort
            The emitted event of the close short call.
        """
        return self._pool._close_short(self.agent, maturity_time, bonds)

    def add_liquidity(self, base: FixedPoint) -> AddLiquidity:
        """Adds liquidity for this agent.

        Arguments
        ---------
        base: FixedPoint
            The amount of liquidity to add in units of base.

        Returns
        -------
        AddLiquidity
            The emitted event of the add liquidity call.
        """
        return self._pool._add_liquidity(self.agent, base)

    def remove_liquidity(self, shares: FixedPoint) -> RemoveLiquidity:
        """Removes liquidity for this agent.

        Arguments
        ---------
        shares: FixedPoint
            The amount of liquidity to remove in units of shares.

        Returns
        -------
        RemoveLiquidity
            The emitted event of the remove liquidity call.
        """
        return self._pool._remove_liquidity(self.agent, shares)

    def redeem_withdraw_share(self, shares: FixedPoint) -> RedeemWithdrawalShares:
        """Redeems withdrawal shares for this agent.

        Arguments
        ---------
        shares: FixedPoint
            The amount of withdrawal shares to redeem in units of shares.

        Returns
        -------
        RedeemWithdrawalShares
            The emitted event of the redeem withdrawal shares call.
        """
        return self._pool._redeem_withdraw_share(self.agent, shares)

    def execute_policy_action(
        self,
    ) -> list[OpenLong | OpenShort | CloseLong | CloseShort | AddLiquidity | RemoveLiquidity | RedeemWithdrawalShares]:
        """Executes the underlying policy action (if set).

        Returns
        -------
        list[OpenLong | OpenShort | CloseLong | CloseShort | AddLiquidity | RemoveLiquidity | RedeemWithdrawalShares]
            Events of the executed actions.
        """
        return self._pool._execute_policy_action(self.agent)

    def liquidate(
        self, randomize: bool = False
    ) -> list[CloseLong | CloseShort | RemoveLiquidity | RedeemWithdrawalShares]:
        """Liquidate all of the agent's positions.

        Arguments
        ---------
        randomize: bool, optional
            Whether to randomize liquidation trades. Defaults to False.

        Returns
        -------
        list[CloseLong | CloseShort | RemoveLiquidity | RedeemWithdrawalShares]
            Events of the executed actions.
        """
        return self._pool._liquidate(self.agent, randomize)
