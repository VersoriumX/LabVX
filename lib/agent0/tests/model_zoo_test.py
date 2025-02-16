"""Test the agent0 model zoo."""
from __future__ import annotations

import logging

from agent0.hyperdrive.policies.zoo import Random, Zoo


class TestModelZoo:
    """Test model zoo."""

    def test_describe_all(self):
        """Test zoo's describe method for all agents."""
        str_output = "Testing describe all\n"
        zoo = Zoo()  # pylint: disable=no-member
        zoo_description = zoo.describe()
        str_output += zoo_description
        logging.info(str_output)

    def test_describe_single(self):
        """Test zoo's describe method for a single agent."""
        str_output = "Testing describe single\n"
        zoo = Zoo()  # pylint: disable=no-member
        zoo_description = zoo.describe("random")
        str_output += zoo_description
        logging.info(str_output)

    def test_description(self):
        """Test the description method for a single agent."""
        str_output = "Testing description\n"
        zoo_description = Random.description()  # access class method
        str_output += zoo_description
        logging.info(str_output)
