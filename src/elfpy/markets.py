"""
Market simulators store state information when interfacing AMM pricing models with users
"""

# Currently many functions use >5 arguments.
# These should be packaged up into shared variables, e.g.
#     reserves = (in_reserves, out_reserves)
#     share_prices = (init_share_price, share_price)
# pylint: disable=too-many-arguments


class Market:
    """
    Holds state variables for market simulation and executes trades.

    The Market class executes trades by updating market variables according to the given pricing model.
    It also has some helper variables for assessing pricing model values given market conditions.
    """

    # TODO: set up member object that owns attributes instead of so many individual instance attributes
    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        base_asset,
        token_asset,
        fee_percent,
        time_remaining,
        pricing_model,
        init_share_price=1,
        share_price=1,
        verbose=False,
    ):
        self.base_asset = base_asset  # x
        self.token_asset = token_asset  # y
        self.fee_percent = fee_percent  # g
        self.time_remaining = time_remaining  # t
        self.share_price = share_price  # c
        self.init_share_price = init_share_price  # u normalizing constant
        self.pricing_model = pricing_model
        self.base_asset_orders = 0
        self.token_asset_orders = 0
        self.base_asset_volume = 0
        self.token_asset_volume = 0
        self.cum_token_asset_slippage = 0
        self.cum_base_asset_slippage = 0
        self.cum_token_asset_fees = 0
        self.cum_base_asset_fees = 0
        self.total_supply = self.base_asset + self.token_asset
        self.verbose = verbose

    def apy(self, days_remaining):
        """Returns current APY given the market conditions and pricing model"""
        price = self.pricing_model.calc_spot_price_from_reserves(
            self.base_asset,
            self.token_asset,
            self.total_supply,
            self.time_remaining,
            self.init_share_price,
            self.share_price,
        )
        normalized_days_remaining = self.pricing_model.norm_days(days_remaining)
        return self.pricing_model.calc_apy_from_spot_price(price, normalized_days_remaining)

    def spot_price(self):
        """Returns the current spot price given the market conditions and pricing model"""
        return self.pricing_model.calc_spot_price_from_reserves(
            self.base_asset,
            self.token_asset,
            self.total_supply,
            self.time_remaining,
            self.init_share_price,
            self.share_price,
        )

    def tick(self, step_size):
        """
        Decrements the time variable by the provided step_size.

        Arguments:
        step_size [float] must be less than self.time_remaining

        It is assumed that self.time_remaining starts at 1 and decreases to 0.
        This function cannot reduce self.time_remaining below 0.
        """

        self.time_remaining -= step_size
        if self.time_remaining < 0:
            assert False, (
                f"ERROR: the time variable market.time_remaining={self.time_remaining} should never be negative."
                + f"\npricing_model={self.pricing_model}"
            )

    def check_fees(
        self,
        amount,
        direction,
        tokens,
        reserves,
        trade_results,
    ):
        """Checks fee values for out of bounds and prints verbose outputs"""
        (token_in, token_out) = tokens
        (in_reserves, out_reserves) = reserves
        (
            without_fee_or_slippage,
            output_with_fee,
            output_without_fee,
            fee,
        ) = trade_results
        if (
            any(
                [
                    isinstance(output_with_fee, complex),
                    isinstance(output_without_fee, complex),
                    isinstance(fee, complex),
                ]
            )
            or fee < 0
        ):
            state_string = self.get_market_state_string()
            assert False, (
                f"Market.check_fees: Error: fee={fee} should not be < 0 and the type should not be complex."
                + f"\ntoken_in = {token_in}"
                + f"\ntoken_out = {token_out}"
                + f"\ndirection = {direction}"
                + f"\nin_reserves = {in_reserves}"
                + f"\nout_reserves = {out_reserves}"
                + f"\ntrade_amount = {amount}"
                + f"\nwithout_fee_or_slippage = {without_fee_or_slippage}"
                + f"\noutput_with_fee = {output_with_fee}"
                + f"\noutput_without_fee = {output_without_fee}\n"
                + state_string
            )

    def update_market(self, d_asset, d_slippage, d_fees, d_orders, d_volume):
        """
        Increments member variables to reflect current market conditions

        All arguments are tuples containing the (base, token) adjustments for each metric
        """
        self.base_asset += d_asset[0]
        self.token_asset += d_asset[1]
        self.cum_base_asset_slippage += d_slippage[0]
        self.cum_token_asset_slippage += d_slippage[1]
        self.cum_base_asset_fees += d_fees[0]
        self.cum_token_asset_fees += d_fees[1]
        self.base_asset_orders += d_orders[0]
        self.token_asset_orders += d_orders[1]
        self.base_asset_volume += d_volume[0]
        self.token_asset_volume += d_volume[1]

    def swap(self, amount, direction, token_in, token_out):
        """
        Execute a trade in the simulated market.

        Arguments:
        amount [float] volume to be traded, in units of the target asset
        direction [str] either "in" or "out"
        token_in [str] either "fyt" or "base" -- must be the opposite of token_out
        token_out [str] either "fyt" or "base" -- must be the opposite of token_in

        Fees are computed, as well as the adjustments in asset volume.
        All internal market variables are updated from the trade.

        """
        # TODO: Simplify the logic by forcing token_out to always equal the opposite of token_in
        # TODO: Break this function up to use private class functions
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        if direction == "in":
            if token_in == "fyt" and token_out == "base":
                in_reserves = self.token_asset + self.total_supply
                out_reserves = self.base_asset
                trade_results = self.pricing_model.calc_in_given_out(
                    amount,
                    in_reserves,
                    out_reserves,
                    token_in,
                    self.fee_percent,
                    self.time_remaining,
                    self.init_share_price,
                    self.share_price,
                )
                (
                    without_fee_or_slippage,
                    output_with_fee,
                    output_without_fee,
                    fee,
                ) = trade_results
                d_base_asset = -output_with_fee
                d_token_asset = amount
                d_base_asset_slippage = abs(without_fee_or_slippage - output_without_fee)
                d_token_asset_slippage = 0
                d_base_asset_fee = 0
                d_token_asset_fee = fee
                d_base_asset_orders = 1
                d_token_asset_orders = 0
                d_base_asset_volume = output_with_fee
                d_token_asset_volume = 0
            elif token_in == "base" and token_out == "fyt":
                in_reserves = self.base_asset
                out_reserves = self.token_asset + self.total_supply
                trade_results = self.pricing_model.calc_in_given_out(
                    amount,
                    in_reserves,
                    out_reserves,
                    token_in,
                    self.fee_percent,
                    self.time_remaining,
                    self.init_share_price,
                    self.share_price,
                )
                (
                    without_fee_or_slippage,
                    output_with_fee,
                    output_without_fee,
                    fee,
                ) = trade_results
                d_base_asset = amount
                d_token_asset = -output_with_fee
                d_base_asset_slippage = 0
                d_token_asset_slippage = abs(without_fee_or_slippage - output_without_fee)
                d_base_asset_fee = fee
                d_token_asset_fee = 0
                d_base_asset_orders = 0
                d_token_asset_orders = 1
                d_base_asset_volume = 0
                d_token_asset_volume = output_with_fee
            else:
                raise ValueError(
                    "token_in and token_out must be unique and in the set ('base', 'fyt'), "
                    + f"not in={token_in} and out={token_out}"
                )
        elif direction == "out":
            if token_in == "fyt" and token_out == "base":
                in_reserves = self.token_asset + self.total_supply
                out_reserves = self.base_asset
                trade_results = self.pricing_model.calc_out_given_in(
                    amount,
                    in_reserves,
                    out_reserves,
                    token_out,
                    self.fee_percent,
                    self.time_remaining,
                    self.init_share_price,
                    self.share_price,
                )
                (
                    without_fee_or_slippage,
                    output_with_fee,
                    output_without_fee,
                    fee,
                ) = trade_results
                d_base_asset = -output_with_fee
                d_token_asset = amount
                d_base_asset_slippage = abs(without_fee_or_slippage - output_without_fee)
                d_token_asset_slippage = 0
                d_base_asset_fee = fee
                d_token_asset_fee = 0
                d_base_asset_orders = 1
                d_token_asset_orders = 0
                d_base_asset_volume = output_with_fee
                d_token_asset_volume = 0
            elif token_in == "base" and token_out == "fyt":
                in_reserves = self.base_asset
                out_reserves = self.token_asset + self.total_supply
                trade_results = self.pricing_model.calc_out_given_in(
                    amount,
                    in_reserves,
                    out_reserves,
                    token_out,
                    self.fee_percent,
                    self.time_remaining,
                    self.init_share_price,
                    self.share_price,
                )
                (
                    without_fee_or_slippage,
                    output_with_fee,
                    output_without_fee,
                    fee,
                ) = trade_results
                d_base_asset = amount
                d_token_asset = -output_with_fee
                d_base_asset_slippage = 0
                d_token_asset_slippage = abs(without_fee_or_slippage - output_without_fee)
                d_base_asset_fee = 0
                d_token_asset_fee = fee
                d_base_asset_orders = 0
                d_token_asset_orders = 1
                d_base_asset_volume = 0
                d_token_asset_volume = output_with_fee
        else:
            raise ValueError(f'direction argument must be "in" or "out", not {direction}')
        self.check_fees(
            amount,
            direction,
            (token_in, token_out),
            (in_reserves, out_reserves),
            trade_results,
        )
        self.update_market(
            (d_base_asset, d_token_asset),
            (d_base_asset_slippage, d_token_asset_slippage),
            (d_base_asset_fee, d_token_asset_fee),
            (d_base_asset_orders, d_token_asset_orders),
            (d_base_asset_volume, d_token_asset_volume),
        )
        return (without_fee_or_slippage, output_with_fee, output_without_fee, fee)

    def get_market_state_string(self):
        """Returns a formatted string containing all of the Market class member variables"""
        strings = [f"{attribute} = {value}" for attribute, value in self.__dict__.items()]
        state_string = "\n".join(strings)
        return state_string
