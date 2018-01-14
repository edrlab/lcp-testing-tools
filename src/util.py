# -*- coding: utf-8 -*-

"""
Utilities
"""

import subprocess
import os.path
import logging

LOGGER = logging.getLogger(__name__)



def init_logger(verbosity):
    """Globally update logger

    - change formatter
    - set verbosity level"""

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    level = {
        0: "ERROR",
        1: "WARNING",
        2: "INFO",
        3: "DEBUG"
    }.get(verbosity, "ERROR")
    logger.setLevel(level)


def execute_command(cmd, cwd=None):
    """
    Helper to execute command

    Returns
        (int, str, str): (return code, stdout, stderr)
    """
    cwd_abs_path = None

    if cwd is not None:
        cwd_abs_path = os.path.abspath(cwd)

    process = subprocess.Popen(
        cmd, cwd=cwd_abs_path,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

