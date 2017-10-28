# -*- coding: utf-8 -*-

"""
Base Test suite
"""

import logging

from exception import TestSuiteLogicError, TestSuiteRunningError

LOGGER = logging.getLogger(__name__)

class BaseTestSuite:
    """Base test suite"""

    def get_tests(self):
        """List of tests to execute"""

        raise NotImplementedError("No tests defined")

    def run(self):
        """
        Run all tests
        """

        # Check that all test methods exist
        test_methods = []

        for name in self.get_tests():
            method_name = "test_" + name

            if not hasattr(self, method_name):
                raise TestSuiteLogicError("Method does not exist", method_name)

            test_methods.append(method_name)

        try:
            # Initialize tests
            LOGGER.debug("Initialization start")
            self.initialize()
            LOGGER.debug("Initialization end")

            # Run every test
            for method_name in test_methods:
                LOGGER.info("Test start: %s", method_name)
                method = getattr(self, method_name)
                method()
                LOGGER.debug("Test succeeded")
        except TestSuiteRunningError as err:
            LOGGER.error(err)
            return False
        finally:
            # Clean tests
            LOGGER.debug("Finalize start")
            self.finalize()
            LOGGER.debug("Finalize end")

        return True

    def initialize(self):
        """
        Initialize tests
        """

        pass

    def finalize(self):
        """
        Finalize/clean tests
        """

        pass
