# -*- coding: utf-8 -*-

"""
Custom exceptions
"""

class ConfigParseError(Exception):
    """Occurs during config parsing"""
    pass


class TestSuiteLogicError(Exception):
    """Occurs if there is a logic error in TestSuite"""
    pass

class TestSuiteRunningError(Exception):
    """Occurs during TestSuite test"""
    pass

class LCPLicenseError(Exception):
    """Occurs during LCP license handling"""
    pass

class LCPCmdError(Exception):
    """Occurs during LCP license handling"""
    pass
