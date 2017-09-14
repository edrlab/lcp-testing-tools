# -*- coding: utf-8 -*-

"""
License Test suite

Copyright EDRLab, 2017

Check an LCP license file

"""

import logging
import hashlib
import json
import jsonschema
import os
import uuid
import subprocess
from base_test_suite import BaseTestSuite
from exception import TestSuiteRunningError

LOGGER = logging.getLogger(__name__)

JSON_SCHEMA_DIR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schema')

class LCPLTestSuite(BaseTestSuite):
    """License test suite"""

    def __init__(self, config_manager, license_path):
        """
        Args:
            config_manager (ConfigManager): ConfigManager object
            license_path (str): Path to an LCP license file to test
        """

        self.config_manager = config_manager
        self.license_path = license_path

        # LCP License
        self.lcpl = None


    def test_validate_lcpl(self):
        """
        Validate an LCP license file
        """

        # validate the license using the JSON schema, includes:
        # check the profile Value (basic or 1.0)
        # check the encryption method (aes-cbc), user key (sha256) and signature algorithm (ecdsa-sha256)

        lcpl_json_schema_path = os.path.join(
            JSON_SCHEMA_DIR_PATH, 'lcpl_schema.json')

        with open(lcpl_json_schema_path) as schema_file:
            lcpl_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lcpl, lcpl_json_schema, format_checker=jsonschema.FormatChecker())
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

    def test_required_links(self):
        # check the presence of rel="hint"" and "publication"" links, required by the specification.
        # check the mime-type of a publication link.
        # such constraints appear un-checkable with a json schema.
        res = 0
        for l in self.lcpl['links']:
            if l['rel'] == 'hint':
                res +=1
            if l['rel'] == 'publication':
                if l['type'] != None and l['type'] != "application/epub+zip":
                    raise TestSuiteRunningError(
                        "A 'publication' link must have an 'application/epub+zip' type")              
                res +=1
        if res != 2:
            raise TestSuiteRunningError(
                "Missing 'hint' or 'publication' link in the license file")

        
           
        pass

    def test_content_key(self):
        # check the content key value, using openssl (no line break, 60 bytes) 
        # cf 2.1.4.5
        # cat license.lcpl | jq -r .encryption.content_key.encrypted_value | openssl enc -d -base64 -A | wc -c
        pass

    def test_key_check(self):
        # check the key_check value (base64 decoded key_check value = cleartext id value)
        # cf 2.1.4.5
        # cat license.lcpl | jq -r .encryption.user_key.key_check | openssl enc -d -base64 -A | wc -c
        # to compare with $(cat license.lcpl | jq -r .id | wc -c) + 28
        pass

    def test_user_info(self):
        # check the encrypted user properties (using the passphrase, finding the user key 
        # through the passphrase->user-key algorithm, then decrypting the info via the user key
        # and the encryption algorithm identified in the encryption/content_key)
        # cf 2.1.4.7
        pass

    def test_signature(self):
        # check the signature value using the java signature tool
        # this java code returns 1 if the signature is not valid 
        cert_path = self.config_manager.root_cert_path
        if not os.path.exists(cert_path):
            raise TestSuiteRunningError(
                "Root certificate file {0} not found".format(cert_path))
            
        run_script = '../SignatureVerifier_Java/run-from-py.sh' if os.name == 'posix' else '../SignatureVerifier_Java/run-from-py.bat'
        run_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), run_script)
            
        args = [run_path, cert_path, self.license_path]
        r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if r.returncode > 0:
            raise TestSuiteRunningError(r.stdout.strip())
        LOGGER.debug(r.stdout.strip())

    def test_encrypted_resources(self):
        # check the each encrypted resource is correctly encrypted and compressed 
        pass

        
    def initialize(self):
        """Initialize tests"""

        if not os.path.exists(self.license_path):
            raise TestSuiteRunningError(
                "License file {0} not found".format(self.license_path))
        
        with open(self.license_path) as json_file:    
            self.lcpl = json.load(json_file)

        # check that the license is utf-8 encoded


    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "validate_lcpl",
            "required_links",
            "content_key",
            "key_check",
            "user_info",
            #"signature",
            "encrypted_resources"
            ]
