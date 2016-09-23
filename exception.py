# -*- coding: utf-8 -*-
class TestManagerInitializationError(Exception):
    """Occurs during TestManager initialization"""

    pass

class TestSuiteInitializationError(Exception):
    """Occurs during TestSuite initialization"""

    pass

class TestSuiteRunningError(Exception):
    """Occurs during TestSuite test"""

    pass
