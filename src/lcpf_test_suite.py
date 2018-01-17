# -*- coding: utf-8 -*-

"""
Check an LCP Protected publication, retrieve a license from the file.

Copyright 2017 European Digital Reading Lab. All rights reserved.
Licensed to the Readium Foundation under one or more contributor license agreements.
Use of this source code is governed by a BSD-style license
that can be found in the LICENSE file exposed on Github (readium) in the project repository.
"""

import logging
import os.path
import zipfile
import util

from lxml import etree
from exception import TestSuiteRunningError
from base_test_suite import BaseTestSuite

LOGGER = logging.getLogger(__name__)

class LCPFTestSuite(BaseTestSuite):
    """LCP Protected file test suite"""

    def __init__(self, config, file_path):
        """
        Args:
            config (TestConfig): Configuration object
            file_path (str): Path to a protected publication (epub+lcpl)
        """

        self.config = config
        self.file_path = file_path

        # To be used by subsequent tests
        # the target folder name will get '-', not '.'
        self.target_path = os.path.join(self.config.working_path, 
                                os.path.basename(self.file_path).replace('.','-'))

        self.license_path = None

    def initialize(self):
        """Initialize tests"""

        if not os.path.exists(self.file_path):
            raise TestSuiteRunningError(
                "The protected publication does not exist {0}".format(self.file_path))


    def test_validate_encryption_xml(self):
        """
        Check if encryption.xml is present in the protected publication
        Validate the xml file.
        """

        try:
            with zipfile.ZipFile(self.file_path) as zip:
                # it will store the xml file in the working dir, in a subfolder named after the protected publication
                encryption_file = zip.extract('META-INF/encryption.xml', self.target_path)
        except KeyError as err:
            raise TestSuiteRunningError(err)

        """
        The W3C schema checks the following rules:
        * In each EncryptedData element:
        - The encryption method must be (aes256-cbc) (LCP profile basic and 1.0)     
        - The ds:KeyInfo element MUST point to the Content Key using the ds:RetrievalMethod element.
        - The URI attribute of ds:RetrievalMethod MUST use a value of “license.lcpl#/encryption/content_key” to point to the encrypted Content Key stored in the License Document. 
        - The Type attribute MUST use a value of “http://readium.org/2014/01/lcp#EncryptedContentKey” to identify the target of the URI as an encrypted Content Key.
        """
        try:
            schema = etree.parse(self.config.encryption_schema)
        except OSError as err:
            raise TestSuiteRunningError(err)
            
        xsd = etree.XMLSchema(schema)

        doc = etree.parse(os.path.join(self.target_path, 'META-INF/encryption.xml'))
        if not xsd.validate(doc):
            for error in xsd.error_log:
                print (error.message, error.line, error.column)
            raise TestSuiteRunningError("encryption.xml is invalid")

    def test_check_encrypted_resources(self):
        """
        Check if all resources referenced in encryption.xml
        are found in the EPUB archive.
        """
               
        doc = etree.parse(os.path.join(self.target_path, 'META-INF/encryption.xml'))
        # list all encrypted resources in encryption.xml
        enc_res = doc.xpath("/c:encryption/e:EncryptedData/e:CipherData/e:CipherReference/@URI", 
            namespaces={'c':'urn:oasis:names:tc:opendocument:xmlns:container',
                        'e':'http://www.w3.org/2001/04/xmlenc#'})

        try:
            with zipfile.ZipFile(self.file_path) as zip:
                for r in enc_res:
                    info = zip.getinfo(r)
                    #print(info)
        except KeyError as err:
            raise TestSuiteRunningError(err)

        """
        The following resource MUST NOT be encrypted:
         - mimetype, META-INF/container.xml, META-INF/encryption.xml, META-INF/license.lcpl, META-INF/manifest.xml, META-INF/metadata.xml, META-INF/rights.xml, META-INF/signatures.xml 
         - and also any navigation document, ncx document or cover image found in the archive
            nb : to check the resource type, the .opf must be checked also.
        """
        disjoint = set(enc_res).isdisjoint(['mimetype', 'META-INF/container.xml', 'META-INF/encryption.xml', 'META-INF/license.lcpl', 'META-INF/manifest.xml', 'META-INF/metadata.xml', 'META-INF/rights.xml', 'META-INF/signatures.xml'])
        if not disjoint:
            raise TestSuiteRunningError("A resource that must not be encrypted is present in encryption.xml")

        # Media resources SHOULD NOT be compressed => Compression/@Method != 8
        cmp_res = doc.xpath("/c:encryption/e:EncryptedData[e:EncryptionProperties/e:EncryptionProperty/cp:Compression[@Method='8']]/e:CipherData/e:CipherReference/@URI", 
            namespaces={'c':'urn:oasis:names:tc:opendocument:xmlns:container',
                        'e':'http://www.w3.org/2001/04/xmlenc#',
                        'cp':'http://www.idpf.org/2016/encryption#compression'})
        for r in cmp_res:
            if r.endswith(('.jpg','.png','.gif','.mp3')):
                raise TestSuiteRunningError("{0} should not be compressed in encryption.xml".format(r))
        

    def test_check_license_lcpl(self):
        """
        Check if license.lcpl is present in the protected publication
        Extract license.lcpl (as license_path)
        """

        try:
            with zipfile.ZipFile(self.file_path) as zip:
                self.license_path = zip.extract('META-INF/license.lcpl', self.target_path)
        except KeyError as err:
            raise TestSuiteRunningError(err)

    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "validate_encryption_xml",
            "check_encrypted_resources",
            "check_license_lcpl"
            ]
