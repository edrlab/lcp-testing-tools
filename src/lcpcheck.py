# -*- coding: utf-8 -*-

"""
Client test launcher
"""

import argparse
import sys
import logging

import util
from chkconfig import TestConfig
from lcpf_test_suite import LCPFTestSuite
from lcpl_test_suite import LCPLTestSuite
from lsd_test_suite import LSDTestSuite

LOGGER = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")
    parser.add_argument("-c", "--config", help="path to the yaml configuration file")
    parser.add_argument("-f", "--file", nargs='?', const='-', help="check a protected file, retrieve a license.")
    parser.add_argument("-l", "--lcpl", nargs='?', const='-', help="check an LCP license; don't give the path to an LCP license if -f  is used")
    parser.add_argument("-s", "--lsd", nargs='?', const='-', help="launch lsd tests; don't give the path to an LCP license if -f or -l is used")
    args = parser.parse_args()

    # Initialize logger 
    util.init_logger(args.verbosity)

    # Load the configuration file
    try:
        config = TestConfig(args.config)
    except FileNotFoundError as err:
        LOGGER.error(err)
        return 1
    
    license_path = ""
        
    # Check a protected file, retrieve a license
    if args.file:
        # use the file argument value
        file_path = args.file
        lcpf_test_suite = LCPFTestSuite(config, file_path)
        if not lcpf_test_suite.run():
            return 2
        license_path = lcpf_test_suite.license_path
            
    # Check an LCP license
    if args.lcpl:
        # the lcpl argument value takes precedence over the preceding license_path value
        license_path = args.lcpl if args.lcpl != "-"  else license_path
        lcpl_test_suite = LCPLTestSuite(config, license_path)
        if not lcpl_test_suite.run():
            return 3

    # Check a License Status Document
    # the lsd argument value takes precedence over the lcpl test return
    if args.lsd:
        license_path = args.lsd if args.lsd != "-" else license_path
        lsd_test_suite = LSDTestSuite(config, license_path)
        if not lsd_test_suite.run():
            return 4

    return 0

if __name__ == "__main__":
    sys.exit(main())

