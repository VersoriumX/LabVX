"""Script to format on-chain hyperdrive pool, config, and transaction data post-processing."""
from __future__ import annotations

from chainsync.exec import acquire_data
from hyperlogs import setup_logging

if __name__ == "__main__":
    setup_logging(".logging/acquire_data.log", log_stdout=True)
    acquire_data()
