# -*- coding: utf-8 -*-

"""
LCP Test suite
"""

import logging
import datetime
import hashlib
import json
import os.path
import uuid
from base_test_suite import BaseTestSuite

import util
from exception import TestSuiteRunningError

LOGGER = logging.getLogger(__name__)
DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"

class LCPTestSuite(BaseTestSuite):
    """LCP test suite"""

    def __init__(self, config_manager, epub_path):
        """
        Test an epub file

        Args:
            config_manager (ConfigManager): ConfigManager object
            epub_path (str): Path to an epub file to test
        """

        self.config_manager = config_manager
        self.epub_path = epub_path
        self.lcp_client = util.HttpClient(config_manager.lcp_server)

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

        # To be used by other test suites (LSD, ...)
        self.publication_path = None
        self.license_path = None

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
            }
        }

        return partial_license

    def test_encrypt_epub(self):
        """
        Encrypt an epub file using lcpencrypt command line
        """

        LOGGER.info("Encrypt epub: %s", self.epub_path)

        # Generate new content id
        content_id = str(uuid.uuid4())
        filename, file_extension = os.path.splitext(
            os.path.basename(self.epub_path)
        )
        output_filename = "{0}-{1}{2}".format(
            filename, content_id, file_extension
        )
        output_file_path = os.path.join(
            self.config_manager.lcp_server.external_repository_path, output_filename
        )

        return_code, stdout, stderr = util.execute_command([
            self.config_manager.encrypt_cmd_path,
            '-input', self.epub_path,
            '-contentid', content_id,
            '-output', output_file_path])

        if return_code != 0:
            raise TestSuiteRunningError(stderr)

        LOGGER.debug(stdout)
        result = json.loads(stdout.decode("utf-8"))

        self.encrypted_epub_content_id = result["content-id"]
        self.encrypted_epub_content_key = result["content-encryption-key"]
        self.encrypted_epub_filename = os.path.basename(
            result["protected-content-location"])

    def test_store_encrypted_epub(self):
        """Register encrypted epub into"""

        LOGGER.info("Store encypted epub: %s", self.encrypted_epub_filename)

        internal_encrypted_epub_path = os.path.join(
            self.config_manager.lcp_server.internal_repository_path,
            self.encrypted_epub_filename)

        # Prepare request
        url = "/contents/{0}".format(self.encrypted_epub_content_id)
        body = json.dumps({
            "content-id": self.encrypted_epub_content_id,
            "content-encryption-key": self.encrypted_epub_content_key,
            "protected-content-location": internal_encrypted_epub_path
        })

        # Send request
        response = self.lcp_client.do_request("PUT", url, body)

        if response.status not in (200, 201):
            raise TestSuiteRunningError(
                "Unable to store encrypted epub. Http status code: {0}".format(
                    response.status))

        response_body = response.read()
        LOGGER.debug("Response body: %s", response_body)

    def test_create_license(self):
        """Create a license for the previous stored encrypted epub"""

        LOGGER.info("Create license for %s", self.encrypted_epub_content_id)

        # Prepare request
        url = "/contents/{0}/licenses".format(self.encrypted_epub_content_id)
        body = json.dumps(self.__build_partial_license())

        # Send request
        response = self.lcp_client.do_request("POST", url, body)

        if response.status != 201:
            raise TestSuiteRunningError(
                "Unable to create license. Http status code: {0}".format(
                    response.status))

        # Store license in working path
        response_body = ""
        filename = "{0}.lcpl".format(self.encrypted_epub_content_id)
        file_path = os.path.join(self.config_manager.working_path, filename)

        with open(file_path, 'wb') as file:
            while not response.closed:
                buffer = response.read(2**12) # 4Kbytes

                if len(buffer) == 0:
                    break

                response_body += buffer.decode("utf-8")
                file.write(buffer)

        self.license_path = file_path
        LOGGER.info("License stored in %s", file_path)
        LOGGER.debug("Response body: %s", response_body)

    def test_create_publication(self):
        """Create a publication of the previous stored encrypted epub"""

        LOGGER.info("Create publication for %s", self.encrypted_epub_content_id)

        # Prepare request
        url = "/contents/{0}/publications".format(self.encrypted_epub_content_id)
        body = json.dumps(self.__build_partial_license())

        # Send request
        response = self.lcp_client.do_request("POST", url, body)

        if response.status != 201:
            raise TestSuiteRunningError(
                "Unable to create publication. Http status code: {0}".format(
                    response.status))

        # Store publication in working path
        filename = "{0}.epub".format(self.encrypted_epub_content_id)
        file_path = os.path.join(self.config_manager.working_path, filename)

        with open(file_path, 'wb') as file:
            while not response.closed:
                buffer = response.read(2**12)

                if len(buffer) == 0:
                    break

                file.write(buffer) # 4Kbytes

        self.publication_path = file_path
        LOGGER.info("Publication stored in %s", file_path)

    def initialize(self):
        """Initialize tests"""

        if not os.path.exists(self.epub_path):
            raise TestSuiteRunningError(
                "Epub file does not exist {0}".format(self.epub_path))

    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "encrypt_epub",
            "store_encrypted_epub",
            "create_license",
            "create_publication"
            ]
