"""Helper class for storing Hyperdrive addresses"""
from __future__ import annotations

import logging
import time

import attr
import requests
from eth_typing import Address, ChecksumAddress

from hypertypes.utilities.conversions import camel_to_snake


@attr.s
class HyperdriveAddresses:
    """Addresses for deployed Hyperdrive contracts."""

    # pylint: disable=too-few-public-methods

    base_token: Address | ChecksumAddress = attr.ib()
    hyperdrive_factory: Address | ChecksumAddress = attr.ib()
    mock_hyperdrive: Address | ChecksumAddress = attr.ib()
    mock_hyperdrive_math: Address | ChecksumAddress | None = attr.ib()


def fetch_hyperdrive_address_from_uri(contracts_uri: str) -> HyperdriveAddresses:
    """Fetch addresses for deployed contracts in the Hyperdrive system.

    Arguments
    ---------
    contracts_uri: str
        The URI for the artifacts endpoint.

    Returns
    -------
    HyperdriveAddresses
        The addresses for deployed Hyperdrive contracts.
    """
    response = None
    for _ in range(100):
        response = requests.get(contracts_uri, timeout=60)
        # Check the status code and retry the request if it fails
        if response.status_code != 200:
            logging.warning(
                "Request for contracts_uri=%s failed with status code %s @ %s",
                contracts_uri,
                response.status_code,
                time.ctime(),
            )
            time.sleep(10)
            continue
        # If successful, exit attempt loop
        break
    if response is None:
        raise ConnectionError("Request failed, returning status `None`")
    if response.status_code != 200:
        raise ConnectionError(f"Request failed with status code {response.status_code} @ {time.ctime()}")
    addresses_json = response.json()

    addresses = HyperdriveAddresses(**{camel_to_snake(key): value for key, value in addresses_json.items()})
    return addresses
