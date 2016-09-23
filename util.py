# -*- coding: utf-8 -*-

import subprocess
import os.path
import logging

class Logger(logging.Logger):
    """Logger with verbosity level"""

    def __init__(self, name, verbosity=0):
        """
        Initialize logger
        """

        super(Logger, self).__init__(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)
        level = {
            0: "ERROR",
            1: "WARNING",
            2: "INFO",
            3: "DEBUG"
        }.get(verbosity, "ERROR")
        self.setLevel(level)

# Helper to execute command
def execute_command(cmd, cwd=None):
    """
    Returns
        (int, str, str): (return code, stdout, stderr)
    """
    cwd_abs_path = None

    if cwd is not None:
        cwd_abs_path = os.path.abspath(cwd)

    p = subprocess.Popen(
        cmd, cwd=cwd_abs_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr
