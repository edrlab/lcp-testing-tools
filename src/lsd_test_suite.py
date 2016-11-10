# -*- coding: utf-8 -*-

"""
LSD Test suite
"""

import json
import logging
import os.path
import urllib.parse

import jsonschema
import util
from exception import TestSuiteRunningError
from base_test_suite import BaseTestSuite

LOGGER = logging.getLogger(__name__)
JSON_SCHEMA_DIR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schema')

class LSDTestSuite(BaseTestSuite):
    """LSD test suite"""

    def __init__(self, config_manager, epub_path, license_path):
        """
        Args:
            config_manager (ConfigManager): ConfigManager object
            epub_path (str): Path to an epub (epub+lcpl)
            license_path (str): Path to an lcpl file
        """

        self.epub_path = epub_path
        self.license_path = license_path
        self.lsd_client = util.HttpClient(config_manager.lsd_server)

        # LCP License
        self.lcpl = None

        # License Status Document
        self.lsd = None

    def _extract_lsd_url(self, lcpl):
        """
        Extract status document url from LCP license

        Args:
            lcpl: lcp license as a json dictionary

        Return:
            json dictionary
        """

        if "links" not in lcpl:
            # No links
            return None

        for link in lcpl['links']:
            if link['rel'] != "status":
                continue

            # Status link
            return link['href']

        # No status link found
        return None

    def _get_lcpl(self, epub_path):
        """
        Returns license document in json

        Args:
            epub_path: Encrypted epub path

        Return:
            json dictionary
        """

        lcpl_content = util.extract_zip_content(
            epub_path, 'META-INF/license.lcpl').decode(encoding='utf-8')
        lcpl = json.loads(lcpl_content)
        LOGGER.debug("LCP license for %s: %s", epub_path, lcpl_content)
        return lcpl


    def _get_lsd(self, url, device_id, device_name):
        """
        Retrieve status document

        Args:
            url: url used to retrieve status document
            device_id: Id of device
            device_name: Name of device
        """

        query_string = urllib.parse.urlencode({
            "device_id": device_id,
            "device_name": device_name
        })
        lsd_url = url + "?" + query_string
        response = self.lsd_client.do_request('GET', lsd_url)
        lsd_content = response.read().decode(encoding='utf-8')
        lsd = json.loads(lsd_content)
        LOGGER.debug("LSD for url %s: %s", lsd_url, lsd_content)
        return lsd

    def test_validate_lsd(self):
        """
        Validate LSD
        """

        lsd_json_schema_path = os.path.join(
            JSON_SCHEMA_DIR_PATH, 'lsd_schema.json')

        with open(lsd_json_schema_path) as schema_file:
            lsd_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lsd, lsd_json_schema)
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

    def initialize(self):
        """Initialize tests"""

        if not os.path.exists(self.epub_path):
            raise TestSuiteRunningError(
                "Epub file does not exist {0}".format(self.epub_path))

        self.lcpl = self._get_lcpl(self.epub_path)
        lsd_url = self._extract_lsd_url(self.lcpl)
        self.lsd = self._get_lsd(lsd_url, "1", "My device")

    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "validate_lsd"
            ]
