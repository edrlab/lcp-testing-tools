# -*- coding: utf-8 -*-

"""
Utilities
"""

from urllib.parse import urlparse
import http.client
import subprocess
import os.path
import logging

LOGGER = logging.getLogger(__name__)

class HttpClient:
    """
    Http Client based on ServerConfig
    """

    def __init__(self, config):
        """Initialize http client

        Args:
            config (BasicServerConfig): server configuration
        """

        self.conn = http.client.HTTPConnection(
            urlparse(config.base_uri).netloc)

        # Prepare base http headers
        self.headers = {
            "Content-Type": "application/json"
        }

        if config.auth_digest is not None:
            # Add authorization header
            self.headers["Authorization"] = "Basic {0}".format(
                config.auth_digest
            )

    def do_request(self, method, url, body=None):
        """Connect to lcp server and do a request

        Args:
            method (string): (GET|PUT|POST|DELETE)
            url (string): url to request
            body: Body to send
        Returns:
            HttpResponse
        """

        headers = self.headers
        LOGGER.debug("Request: %s %s", method, url)
        LOGGER.debug("Request headers: %s", headers)

        if body is not None:
            LOGGER.debug("Request body: %s", body)

        try:
            self.conn.request(method, url, body, headers)
            response = self.conn.getresponse()
            LOGGER.debug("Response status code: %s", response.status)
            LOGGER.debug("Response headers: %s", response.getheaders())

            return response
        # if the server does not responds, an exception ConnectionRefusedError occurs,
        # to be catched by the caller.
        except http.client.CannotSendRequest as err:
            raise ConnectionRefusedError

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

