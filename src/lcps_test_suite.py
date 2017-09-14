# -*- coding: utf-8 -*-

"""
License Server test suite

Copyright EDRLab, 2017

Protect an epub file, retrieve a license and an LCP Protected publication from the server.
Use the Readium Encryption utility and License Server.
The License Server must be running when the tests start.
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

class LCPSTestSuite(BaseTestSuite):
    """EPUB test suite"""

    def __init__(self, config_manager, epub_path):
        """
        Args:
            config_manager (ConfigManager): ConfigManager object
            epub_path (str): Path to an epub file
        """

        self.config_manager = config_manager
        self.epub_path = epub_path
        self.lcp_client = util.HttpClient(config_manager.lcp_server)

        filename, file_extension = os.path.splitext(os.path.basename(epub_path))
        self.epub_filename = filename

        # Protected content information
        self.encrypted_content_id = None
        self.encrypted_content_encryption_key = None
        self.encrypted_content_filename = None
        self.encrypted_content_length= None
        self.encrypted_content_sha256 = None
        self.encrypted_content_disposition = None

        # To be used by subsequent tests
        self.protected_file_path = None
        self.license_path = None

    def __build_partial_license(self):
        """Build partial license

        Returns:
            dict
        """

        # 100 days to read the publication
        license_start_datetime = datetime.datetime.today()
        license_end_datetime = license_start_datetime + \
            datetime.timedelta(days=100)

        # Random provider id
        provider_id = str(uuid.uuid4())
        # Random user id and email
        user_id = str(uuid.uuid4())
        user_email = "{0}@lcp.test.local".format(user_id)

        # Hash the passphrase (computed in the config)
        hash_engine = hashlib.sha256()
        hash_engine.update(self.config_manager.lcp_server.user_passphrase.encode("utf-8"))
        user_passphrase_hex_digest = hash_engine.hexdigest()

        # Prepare a partial license
        partial_license = {
            "provider": provider_id,
            "user": {
                "id": user_id,
                "email": user_email,
                "encrypted": ["email"]
            },
            "encryption": {
                "user_key": {
                    "text_hint": self.config_manager.lcp_server.user_passphrase_hint,
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
        Encrypt an epub file using the *local* lcpencrypt command line
        """

        LOGGER.info("Encrypt epub: %s", self.epub_path)

        # Generate a random content id
        content_id = str(uuid.uuid4())
        # Generate a target file path 
        output_filename = "{0}-{1}.enc.epub".format(
            self.epub_filename, content_id
        )
        output_file_path = os.path.join(
            self.config_manager.lcp_server.external_repository_path, output_filename
        )

        # Execute the encryption using the lcpencrypt utility
        return_code, stdout, stderr = util.execute_command([
            self.config_manager.lcp_encrypt_cmd_path,
            '-input', self.epub_path,
            '-contentid', content_id,
            '-output', output_file_path])

        if return_code != 0:
            raise TestSuiteRunningError(stderr)

        LOGGER.debug(stdout)
        result = json.loads(stdout.decode("utf-8"))

        self.encrypted_content_id = result["content-id"]
        self.encrypted_content_encryption_key = result["content-encryption-key"]
        self.encrypted_content_filename = os.path.basename(
            result["protected-content-location"])
        self.encrypted_content_length= result["protected-content-length"]
        self.encrypted_content_sha256 = result["protected-content-sha256"]
        self.encrypted_content_disposition = result["protected-content-disposition"]

    def test_store_encrypted_content(self):
        """Store the encrypted epub into the License Server"""

        LOGGER.info("Store encrypted epub: %s", self.encrypted_content_filename)

        internal_encrypted_epub_path = os.path.join(
            self.config_manager.lcp_server.internal_repository_path,
            self.encrypted_content_filename)

        # Prepare request
        url = "/contents/{0}".format(self.encrypted_content_id)
        body = json.dumps({
            "content-id": self.encrypted_content_id,
            "content-encryption-key": self.encrypted_content_encryption_key,
            "protected-content-location": internal_encrypted_epub_path,
            "protected-content-length": self.encrypted_content_length,
            "protected-content-sha256": self.encrypted_content_sha256,
            "protected-content-disposition": self.encrypted_content_disposition
        })

        # Send request
        try:
            response = self.lcp_client.do_request("PUT", url, body)

            if response.status not in (200, 201):
                raise TestSuiteRunningError(
                    "Unable to store encrypted epub. Http status code: {0}".format(
                        response.status))

            response_body = response.read()
            LOGGER.debug("Response body: %s", response_body)
        except ConnectionRefusedError as err:
            LOGGER.error("Connection to server failed %s", self.config_manager.lcp_server.base_uri)
            

    def test_generate_license(self):
        """Generate a license for the current epub"""

        LOGGER.info("Generate a license for %s", self.encrypted_content_id)

        # Prepare the request
        url = "/contents/{0}/licenses".format(self.encrypted_content_id)
        body = json.dumps(self.__build_partial_license())

        try:
            # Send the request
            response = self.lcp_client.do_request("POST", url, body)

            if response.status != 201:
                raise TestSuiteRunningError(
                    "Unable to create license. Http status code: {0}".format(
                        response.status))

            # Store the license in the working path
            response_body = ""
            filename = "{0}-{1}.lcpl".format(self.epub_filename, self.encrypted_content_id)
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
        except ConnectionRefusedError as err:
            LOGGER.error("Connection to server failed %s", self.config_manager.lcp_server.base_uri)


    def test_fetch_protected_publication(self):
        """Create a protected publication for the current epub"""

        LOGGER.info("Create a protected publication for %s", self.encrypted_content_id)

        # Prepare request
        url = "/contents/{0}/publications".format(self.encrypted_content_id)
        body = json.dumps(self.__build_partial_license())

        try:
            # Send request
            response = self.lcp_client.do_request("POST", url, body)

            if response.status != 201:
                raise TestSuiteRunningError(
                    "Unable to create publication. Http status code: {0}".format(
                        response.status))

            # Store the protected publication in the working path
            filename = "{0}-{1}.lcp.epub".format(self.epub_filename, self.encrypted_content_id)
            file_path = os.path.join(self.config_manager.working_path, filename)

            with open(file_path, 'wb') as file:
                while not response.closed:
                    buffer = response.read(2**12)

                    if len(buffer) == 0:
                        break

                    file.write(buffer) # 4Kbytes

            self.protected_file_path = file_path
            LOGGER.info("Publication stored in %s", file_path)
        except ConnectionRefusedError as err:
            LOGGER.error("Connection to server failed %s", self.config_manager.lcp_server.base_uri)


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
            "store_encrypted_content",
            "generate_license",
            "fetch_protected_publication"
            ]
