# -*- coding: utf-8 -*-

"""
Client test launcher
"""

import argparse
import sys
import logging

import util
from config import ConfigManager
from lcps_test_suite import LCPSTestSuite
from lcpf_test_suite import LCPFTestSuite
from lcpl_test_suite import LCPLTestSuite
from lsd_test_suite import LSDTestSuite
from exception import ConfigParseError

LOGGER = logging.getLogger(__name__)

def main():
    """
    Client
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("configfile", help="path to the yaml configuration file")
    parser.add_argument("-e", "--epub", help="protect the epub file indicated as value, generate a license and a protected file")
    parser.add_argument("-p", "--pfile", nargs='?', const='-', help="check a protected file, retrieve a license; optional value: path to an LCP protected epub file")
    parser.add_argument("-l", "--lcpl", nargs='?', const='-', help="check an LCP license; optional value: path to an LCP license if -p was not used")
    parser.add_argument("-s","--lsd", nargs='?', const='-', help="launch lsd tests; optional value: path to an LCP license if -p or -l was not used")
    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger 
    util.init_logger(args.verbosity)

    # Load the configuration file
    try:
        config_manager = ConfigManager(args.configfile)
    except ConfigParseError as err:
        LOGGER.error(err)
        return 2
    
    protected_file_path = ""
    license_path = ""

    # Protect an epub file, generate a license and the protected file
    if args.epub:
        lcps_test_suite = LCPSTestSuite(config_manager, args.epub)
        if not lcps_test_suite.run():
            return 3
        # get back the paths to the generated license and protected file
        protected_file_path = lcps_test_suite.protected_file_path
        license_path = lcps_test_suite.license_path
        
    # Check a protected file, retrieve a license
    if args.pfile:
        # the pfile argument value takes precedence over the preceding license_path value
        file_path = args.pfile if args.pfile != "-" else protected_file_path
        lcpf_test_suite = LCPFTestSuite(config_manager, file_path)
        if not lcpf_test_suite.run():
            return 4
        license_path = lcpf_test_suite.license_path
            
    # Check an LCP license
    if args.lcpl:
        # the lcpl argument value takes precedence over the preceding license_path value
        license_path = args.lcpl if args.lcpl != "-"  else license_path
        lcpl_test_suite = LCPLTestSuite(config_manager, license_path)
        if not lcpl_test_suite.run():
            return 5

    # Check a License Status Document
    # the lsd argument value takes precedence over the lcpl test return
    if args.lsd:
        license_path = args.lsd if args.lsd != "-" else license_path
        lsd_test_suite = LSDTestSuite(
            config_manager,
            license_path)
        if not lsd_test_suite.run():
            return 6

    return 0

if __name__ == "__main__":
    sys.exit(main())

