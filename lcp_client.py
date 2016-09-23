# -*- coding: utf-8 -*-

"""
LCP Test suite
"""

import os.path
import http.client
import datetime
from base64 import b64encode
from urllib.parse import urlparse
import sys
import hashlib
import json
import yaml
import uuid
import util
from exception import (
    TestManagerInitializationError,
    TestSuiteInitializationError,
    TestSuiteRunningError)
import argparse

logger = None
DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"

class LCPEpubTestSuite:
    """LCP epub test suite"""

    def __init__(self, manager, epub_path):
        """
        Test an epub file

        Args:
        manager (LCPTestManager): LCPTestManager object
        epub_path (str): Path to an epub file to test
        """

        self.manager = manager
        self.epub_path = epub_path

        if not os.path.exists(self.epub_path):
            raise TestSuiteInitializationError(
                "Epub file does not exist {0}".format(self.epub_path))

        # Encrypted epub information
        self.encrypted_epub_content_id = None
        self.encrypted_epub_content_key = None
        self.encrypted_epub_filename = None

        # Random provider id
        self.provider_id = str(uuid.uuid4())
        self.provider_url = "http://{0}.lcp.test.local".format(self.provider_id)
        self.user_id = str(uuid.uuid4())
        self.user_email = "{0}@lcp.test.local".format(self.user_id)
        self.user_passphrase = str(uuid.uuid4())

    def encrypt_epub(self):
        """
        Encrypt an epub file using lcpencrypt command line
        """

        # Generate new content id
        content_id = str(uuid.uuid4())
        filename, file_extension = os.path.splitext(
            os.path.basename(self.epub_path)
        )
        output_filename = "{0}-{1}{2}".format(
            filename, content_id, file_extension
        )
        output_file_path = os.path.join(
            self.manager.lcp_server_external_repository_path, output_filename
        )

        return_code, stdout, stderr = util.execute_command([
            self.manager.encrypt_cmd_path,
            '-input', self.epub_path,
            '-contentid', content_id,
            '-output', output_file_path])

        if return_code != 0:
            raise TestSuiteRunningError(stderr)

        logger.debug(stdout)
        result = json.loads(stdout.decode("utf-8"))

        self.encrypted_epub_content_id = result["content-id"]
        self.encrypted_epub_content_key = result["content-encryption-key"]
        self.encrypted_epub_filename = os.path.basename(
            result["protected-content-location"])

    def store_encrypted_epub(self):
        """Register encrypted epub into"""

        internal_encrypted_epub_path = os.path.join(
            self.manager.lcp_server_internal_repository_path,
            self.encrypted_epub_filename)

        # Prepare request
        url = "/contents/{0}".format(self.encrypted_epub_content_id)
        body = json.dumps({
            "content-id": self.encrypted_epub_content_id,
            "content-encryption-key": self.encrypted_epub_content_key,
            "protected-content-location": internal_encrypted_epub_path
        })

        # Send request
        response = self.__do_lcp_client_request("PUT", url, body)
        response_body = response.read()
        logger.debug("Response body: {0}".format(response_body))

    def __build_partial_license(self):
        """Build partial license

        Returns:
            dict
        """

        # Hash passphrase
        hash_engine = hashlib.sha256()
        hash_engine.update(self.user_passphrase.encode("utf-8"))
        user_passphrase_hex_digest = hash_engine.hexdigest()

        # Prepare license
        # 100 days to read epub
        license_start_datetime = datetime.datetime.today()
        license_end_datetime = license_start_datetime + \
            datetime.timedelta(days=100)

        partial_license = {
            "provider": self.provider_id,
            "user": {
                "id": self.user_id,
                "email": self.user_email,
                "encrypted": ["email"]
            },
            "encryption": {
            "user_key": {
                "text_hint": "Enter your passphrase",
                "user_hash": user_passphrase_hex_digest,
                "algorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
                }
            },
            "rights": {
                "print": 10,
                "copy": 2048,
                "start": license_start_datetime.\
                    strftime(DEFAULT_DATETIME_FORMAT),
                "end": license_end_datetime.\
                    strftime(DEFAULT_DATETIME_FORMAT)
            },
            "links": {
                "hint": {
                    "href": "{0}/help-on-hints".format(self.provider_url)
                },
                "publication": {
                    "href": "{0}/contents/{1}".format(
                        self.provider_url,
                        self.encrypted_epub_content_id)
                }
            }
        }

        return partial_license

    def create_license(self):
        """Create a license for the previous stored encrypted epub"""

        # Prepare request
        url = "/contents/{0}/licenses".format(self.encrypted_epub_content_id)
        body = json.dumps(self.__build_partial_license())

        # Send request
        response = self.__do_lcp_client_request("POST", url, body)
        response_body = response.read()
        logger.debug("Response body: {0}".format(response_body))

    def create_publication(self):
        """Create a publication of the previous stored encrypted epub"""

        # Prepare request
        url = "/contents/{0}/publications".format(self.encrypted_epub_content_id)
        body = json.dumps(self.__build_partial_license())

        # Send request
        response = self.__do_lcp_client_request("POST", url, body)

    def __do_lcp_client_request(self, method, url, body=None):
        """Connect to lcp server and do a request

        Args:
            method: (GET|PUT|POST|DELETE)
            url: url to request
            body: Body to send
        Returns:
            HttpResponse
        """

        lcp_client = http.client.HTTPConnection(
            urlparse(self.manager.lcp_server_base_uri).netloc)

        # Prepare auth headers
        headers = {
            "Content-Type": "application/json"
        }

        if self.manager.lcp_server_auth_digest is not None:
            # Add authorization header
            headers["Authorization"] = "Basic {0}".format(
                self.manager.lcp_server_auth_digest
            )

        logger.debug("LCP Client request: {0} {1}".format(method, url))
        logger.debug("Request headers: {0}".format(headers))

        if body is not None:
            logger.debug("Request body: {0}".format(body))

        lcp_client.request(method, url, body, headers)
        response = lcp_client.getresponse()
        logger.debug("Response status code: {0}".format(response.status))
        logger.debug("Response headers: {0}".format(response.getheaders()))
        return response

    def run(self):
        """
        Run all tests
        """

        # Encrypt epub
        self.encrypt_epub()

        # Store encrypted epub
        self.store_encrypted_epub()

        # Create license
        self.create_license()

        # Create publication
        self.create_publication()

    def finalize(self):
        """
        Finalize tests
        Clean LCP server
        """

        pass

class LCPTestManager:
    """LCP Test config"""

    def __init__(self, config_path):
        """
        Initialize test manager

        Args:
            config_path (str): Path to the configuration file
        """

        self.encrypt_cmd_path = None
        self.lcp_server_base_uri = None
        self.lcp_server_auth_digest = None
        self.lcp_server_external_repository_path = None
        self.lcp_server_internal_repository_path = None
        self.load_config(config_path)

    def load_config(self, config_path):
        """
        Parse and load configuration file

        Args:
            config_path: Path of configuration file
        """

        if not os.path.exists(config_path):
            raise TestManagerInitializationError(
                "Config file does not exist"
            )

        with open(config_path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as e:
                raise TestManagerInitializationError("config: {0}", e)

            # Get lcpencrypt command path
            try:
                self.encrypt_cmd_path = config['lcp_encrypt']['cmd_path']
            except KeyError:
                raise TestManagerInitializationError(
                    "config: lcp_encrypt.cmd_path not defined")

            if not os.path.exists(self.encrypt_cmd_path):
                raise TestManagerInitializationError(
                    "config: lcp_encrypt.cmd_path does not exist")

            # Get lcp server base uri
            try:
                self.lcp_server_base_uri = config['lcp_server']['base_uri']
            except KeyError:
                raise TestManagerInitializationError(
                    "config: lcp_server.base_uri not defined")

            # Get lcp server external repository path
            try:
                self.lcp_server_external_repository_path = \
                    config['lcp_server']['external_repository_path']
            except KeyError:
                raise TestManagerInitializationError(
                    "config: lcp_server.external_repository_path not defined")

            if not os.path.exists(self.lcp_server_external_repository_path):
                raise TestManagerInitializationError(
                    "config: lcp_server.external_repository_path does not exist")

            # Get lcp server internal repository path
            try:
                self.lcp_server_internal_repository_path = \
                    config['lcp_server']['internal_repository_path']
            except KeyError:
                raise TestManagerInitializationError(
                    "config: lcp_server.internal_repository_path not defined")

            if 'auth' in config['lcp_server']:
                try:
                    user = config['lcp_server']['auth']['user']
                except KeyError:
                    raise TestManagerInitializationError(
                        "config: lcp_server.auth.user not defined")

                try:
                    passwd = config['lcp_server']['auth']['passwd']
                except KeyError:
                    raise TestManagerInitializationError(
                        "config: lcp_server.auth.passwd not defined")

                self.lcp_server_auth_digest = b64encode(
                    bytes(user + ":" + passwd, "utf-8")).decode("ascii")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to the configuration file")
    parser.add_argument("epub", help="path to a clear epub file")
    parser.add_argument(
        "-v", "--verbosity", action="count", help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger

    logger = util.Logger("lcp_client", args.verbosity)

    # Launch test suite
    try:
        test_manager = LCPTestManager(args.config)
    except TestManagerInitializationError as e:
        logger.error(e)
        sys.exit(2)

    try:
        epub_test_suite = LCPEpubTestSuite(test_manager, args.epub)
    except TestSuiteInitializationError as e:
        logger.error(e)
        sys.exit(3)

    return_code = 0

    try:
        epub_test_suite.run()
    except TestSuiteRunningError as e:
        logger.error(e)
        return_code = 3
    finally:
        # Clean tests
        epub_test_suite.finalize()

    sys.exit(return_code)
