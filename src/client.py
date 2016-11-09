# -*- coding: utf-8 -*-

"""
Client to launch tests
"""

import argparse
import sys
import logging

import util
from config import ConfigManager
from lcp_test_suite import LCPTestSuite
from lsd_test_suite import LSDTestSuite
from exception import ConfigParseError

LOGGER = logging.getLogger(__name__)

def main():
    """
    Client
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to the configuration file")
    parser.add_argument("epub", help="path to a clear epub file")
    parser.add_argument(
        "-v", "--verbosity", action="count", help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger
    util.init_logger(args.verbosity)

    # Load configuration file
    try:
        config_manager = ConfigManager(args.config)
    except ConfigParseError as err:
        LOGGER.error(err)
        return 2

    # LCP tests
    lcp_test_suite = LCPTestSuite(config_manager, args.epub)
    if not lcp_test_suite.run():
        return 3

    # LSD tests
    lsd_test_suite = LSDTestSuite(
        config_manager,
        lcp_test_suite.publication_path,
        lcp_test_suite.license_path)
    if not lsd_test_suite.run():
        return 4

    return 0

if __name__ == "__main__":
    sys.exit(main())

