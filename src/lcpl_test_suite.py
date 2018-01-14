# -*- coding: utf-8 -*-

"""
Check an LCP license file

Copyright 2017 European Digital Reading Lab. All rights reserved.
Licensed to the Readium Foundation under one or more contributor license agreements.
Use of this source code is governed by a BSD-style license
that can be found in the LICENSE file exposed on Github (readium) in the project repository.
"""

import logging
import requests
from lcp_license import LCPLicense
from exception import LCPLicenseError, TestSuiteRunningError
from base_test_suite import BaseTestSuite

LOGGER = logging.getLogger(__name__)


class LCPLTestSuite(BaseTestSuite):
    """License test suite"""

    def __init__(self, config, license_path):
        """
        Args:
          config (TestConfig): Configuration object
          license_path (str): Path to an LCP license file to test
        """

        self.config = config
        self.license_path = license_path

        # LCP License
        self.license = None
             
    def initialize(self):
        """Initialize tests"""

        self.license = LCPLicense()
        try:
            self.license.parse(self.license_path)
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)


    def test_validate_license(self):
        # validate the license using a JSON schema
        try:
            self.license.validate(self.config.license_schema_path)
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)
            
        # display some license values
        LOGGER.info("provider {}".format(self.license.l['provider']))
        LOGGER.info("date issued {}, updated {}".format(
            self.license.l['issued'], self.license.l['updated'] if "updated" in self.license.l else "never"))

    def test_required_links(self):
        # check the presence of mandatory links
        try:
            self.license.check_required_links()
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)


    def test_content_key(self):
        # check the format of the content key
        try:
            self.license.check_content_key()
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)


    def test_key_check(self):
        # check the format of the content key
        try:
            self.license.check_key_check(self.config.cmd.user_passphrase)
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)


    def test_user_info(self):
        # check the encrypted user properties (using the passphrase, finding the user key 
        # through the passphrase->user-key algorithm, then decrypting the info via the user key
        # and the encryption algorithm identified in the encryption/content_key)
        # cf 2.1.4.7

        pass


    def test_certificate(self):
        # check the validity of the certificate, relative to the CA and issued datetime.
        pass


    def test_signature(self):
        # check the signature of the license
        cert_path = self.config.cacert
        try:
            self.license.check_signature(cert_path)
        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)


    def test_rights(self):
        # check the rights expressed in the license
        try:
            self.license.rights_copy()
            self.license.rights_print()
            ok = self.license.check_dates()
            if not ok:
                LOGGER.info("To early or too late to access the ebook")

        except LCPLicenseError as err:
            raise TestSuiteRunningError(err)

    def test_hint_resource(self):
        # check that the hint resource is fetchable
        hint_url = self.license.hint_link()
        if not hint_url:
            return
        try:
            r = requests.get(hint_url)
            if r.status_code != requests.codes.ok:
                raise TestSuiteRunningError(
                    "Impossible to fetch the hint resource at {}: error {}".format(
                        hint_url, r.status_code)
                    )
        except requests.exceptions.RequestException as err:
            LOGGER.warning("Impossible to fetch the hint resource")


    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "validate_license",
            "certificate",
            "signature",
            "required_links",
            "content_key",
            #"key_check",
            "user_info",
            "rights",
            "hint_resource"
            ]
