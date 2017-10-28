# -*- coding: utf-8 -*-

"""
LSD Test suite

Copyright EDRLab, 2017

Check the features of a License Document Server.

History
    Created By Cyrille Lebeaupin / EDRLab, 2017
    Includes code from Ahram Oh / DRM Inside, 2016
    Updated by Laurent Le Meur / EDRLab, 2017 

    Note: the requests library was prefered compared over the http.client lib for the sake of clarity of the code.
"""

import json
import logging
import os.path
import datetime
import dateutil.parser
import requests
import jsonschema
import re
from exception import TestSuiteRunningError
from base_test_suite import BaseTestSuite

LOGGER = logging.getLogger(__name__)

JSON_SCHEMA_DIR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schema')

DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"



class LSDTestSuite(BaseTestSuite):
    """LSD test suite"""

    def __init__(self, config_manager, license_path):
        """
        Args:
            config_manager (ConfigManager): ConfigManager object
            license_path (str): Path to an lcpl file
        """

        self.config_manager = config_manager
        self.license_path = license_path

        # LCP License
        self.lcpl = None

        # License Status Document
        self.lsd = None

        # test device id and name
        self.device_id = 0
        self.device_name = ""

    def _extract_lsd_url(self, lcpl):
        """
        Extract the status document url from the LCP license

        Args:
            lcpl: lcp license as a json object

        Return:
            url of the status document
        """

        if "links" not in lcpl:
            # No links
            LOGGER.warning("No links in the license")
            return None

        for link in lcpl['links']:
            if link['rel'] != "status":
                continue

            # Status link
            return link['href']

        # No status link found
        return None

    def _check_datetime_updated(self, field, date_time):
        """
        Check the date related to the status or license update: 
        it should have been updated after a successfull action.
        field values are 'status' or 'license'.
        """
        LOGGER.info("The %s was last updated on: %s", field, self.lsd['updated']['status'])   
        status_datetime = dateutil.parser.parse(date_time)
        td = datetime.timedelta(minutes=10)
        if status_datetime + td < datetime.datetime.now(datetime.timezone.utc):
            LOGGER.warning("Seems that the timestamp was not updated!") 
            raise TestSuiteRunningError("The timestamp was not updated after the action!")


    def test_fetch_lsd(self):
        """
        Fetch a License Status Document

        note about the use of https with Python 3.6+ on OSX:
        read http://stackoverflow.com/questions/27835619/ssl-certificate-verify-failed-error
        => install certificates /Applications/Python\ 3.6/Install\ Certificates.command 

        """
        lsd_url = self._extract_lsd_url(self.lcpl)
        if lsd_url == None:
            raise TestSuiteRunningError("No status document url found in the license")  
      
        try:
            r = requests.get(lsd_url)
            if r.status_code != requests.codes.ok:
                raise TestSuiteRunningError(
                    "Impossible to fetch the License Status Document at {}: error {}".format(
                        lsd_url, r.status_code)
                    )
        except requests.exceptions.RequestException as err:
            raise TestSuiteRunningError(err)
        try:
            self.lsd = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")

        LOGGER.debug("The License Status Document is available")   


    def test_validate_lsd(self):
        """
        Validate a License Status Document
        """

        lsd_json_schema_path = os.path.join(
            JSON_SCHEMA_DIR_PATH, 'lsd_schema.json')

        with open(lsd_json_schema_path) as schema_file:
            lsd_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lsd, lsd_json_schema)
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

        LOGGER.debug("The License Status Document is valid")   

        LOGGER.info("The status of the license is: %s", self.lsd['status'])  
        LOGGER.info("The status was last updated on: %s", self.lsd['updated']['status'])   
        LOGGER.info("The license was last updated on: %s", self.lsd['updated']['license'])   
        LOGGER.info("The user message is: %s", self.lsd['message'])   
        if 'potential_rights' in self.lsd:
            LOGGER.info("The max loan datetime is: %s", self.lsd['potential_rights']['end'])   
        else:
            LOGGER.info("No max loan datetime")  
        if 'events' in self.lsd:
            for event in self.lsd['events']:
                LOGGER.info("Event: type {}, timestamp {}, id {}, name {}".format(
                    event['type'], 
                    event['timestamp'],
                    event['id'],
                    event['name'])
                )   
            

    def test_fetch_license(self):
        """ Fetch a license from the URL found in the status doc, then validates it """

        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'license'))
        except StopIteration as err:
            raise TestSuiteRunningError(
                "Missing a 'license' link in the status document")
        
        license_url = license['href']
        LOGGER.debug("Fetch license at url %s:", license_url)   

        # fetch the license
        r = requests.get(license_url)
        try:
            self.lcpl = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Document")
        LOGGER.debug("The License is available")   

        # validate the license
        lcpl_json_schema_path = os.path.join(
            JSON_SCHEMA_DIR_PATH, 'lcpl_schema.json')

        with open(lcpl_json_schema_path) as schema_file:
            lcpl_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lcpl, lcpl_json_schema, format_checker=jsonschema.FormatChecker())
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

        LOGGER.debug("The up to date License is available and valid")

        # display some license values
        LOGGER.info("date issued {}, updated {}".format(
            self.lcpl['issued'], self.lcpl['updated'] if "updated" in self.lcpl else "never"))
        LOGGER.info("rights print {}, copy {}".format(
            self.lcpl['rights']['print'], self.lcpl['rights']['copy']))
        LOGGER.info("rights start {}, end {}".format(
            self.lcpl['rights']['start'] if "start" in self.lcpl['rights'] else "none", 
            self.lcpl['rights']['end'] if "end" in self.lcpl['rights'] else "none"))
        
    def test_register(self):
        """ Register a device for the current license.
            Check there is no error in case of multiple registering
            Check the error is registering is not possible.
        """
        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'register'))
        except StopIteration as err:
            LOGGER.warning("'register' link missing in the status document")
            return

        # removes the 'blank' part in the templated URL
        register_url = re.sub("{.*?}",'',license['href'])

        LOGGER.debug("Register at url %s", register_url)

        # id and name are required in the LSD spec
        q = {"id": self.device_id, "name": self.device_name}
        r = requests.post(register_url, params=q)

        # check the return code vs the license status
        if r.status_code != requests.codes.ok:
            LOGGER.warning("Error structure: {}".format(r.text))
            if r.status_code == 400:
                if self.lsd['status'] in ["expired", "returned","cancelled","revoked"]:
                    LOGGER.info("The device could not be registered because the license is now unusable (%s)", 
                        self.lsd['status'])
                return
            # other cases are weird    
            raise TestSuiteRunningError(
                "Impossible to register the device at {}: error {}".format(
                    register_url, r.status_code)
                )
        LOGGER.debug("The device was successfully registered")   

        # if the register operation succeeds, 
        # the server MUST return an updated License Status Document
        try:
            self.lsd = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")

        # check that the status date has been updated
        self._check_datetime_updated('status', self.lsd['updated']['status'])


    def test_renew(self):
        """ Renew a license if renewable.
            Check the error if the license is not (or not anymmore) renewable.
        """
        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'renew'))
        except StopIteration as err:
            LOGGER.warning("No 'renew' link in the status document. ok if buy")
            return

        # removes the 'blank' part in the templated URL
        renew_url = re.sub("{.*?}",'',license['href'])

        LOGGER.debug("Renew at url %s", renew_url)
        LOGGER.debug("Current end date: {}".format(self.lcpl['rights']['end']))
        if 'potential_rights' in self.lsd:
            LOGGER.debug("Max end date: %s", self.lsd['potential_rights']['end'])   
            if dateutil.parser.parse(self.lcpl['rights']['end']) == \
                dateutil.parser.parse(self.lsd['potential_rights']['end']):
                LOGGER.info("Max end date reached, impossible to renew")   
                return    
        else:
            LOGGER.info("No max end date indicated")   

        # choice of a number of days for the renewal
        renew_days = 10

        # let's renew for N days after the current end date
        license_end = dateutil.parser.parse(self.lcpl['rights']['end']) + datetime.timedelta(days=renew_days)

        end = license_end.strftime(DEFAULT_DATETIME_FORMAT)

        # id and name are not required by the LSD spec, but let's add them
        q = {"id": self.device_id, "name": self.device_name, "end": end}
        r = requests.put(renew_url, params=q)

        # check the return code vs the license status
        license_status = self.lsd['status']
        if r.status_code != requests.codes.ok:
            LOGGER.warning("Error structure: {}".format(r.text))
            if r.status_code == 403:
                LOGGER.info("Incorrect renewal period; requested end is %s, potential end is %s", 
                    end, self.lsd['potential_rights']['end'])    
                return
            elif r.status_code >= 400 and license_status not in ["active"]:
                LOGGER.info("The publication can't be renewed properly, as the license is in state %s", 
                     license_status)    
                return
           
            # other cases are weird    
            raise TestSuiteRunningError(
                "Impossible to renew the publication at {}: error {}; license status is {}".format(
                    renew_url, r.status_code, license_status)
                )
        LOGGER.debug("The publication was successfully renewed")   

        # if the renew operation succeeds, 
        # the server MUST return an updated License Status Document
        try:
            self.lsd = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")

        # check that the status date has been updated
        self._check_datetime_updated('status', self.lsd['updated']['status'])
        # check that the license date has been updated
        self._check_datetime_updated('license', self.lsd['updated']['license'])
        # check the new status
        if (self.lsd['status'] != 'active') :
              raise TestSuiteRunningError(
                "The new status {} does not fit: must be active".format(self.lsd['status'])
                )
         
        return
    
    def test_return(self):
        """ Return a license if returnable.
            Check the error if the license is not (or not anymmore) returnable.
        """
        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'return'))
        except StopIteration as err:
            LOGGER.warning("No 'return' link in the status document. ok if buy")
            return

        # removes the 'blank' part in the templated URL
        return_url = re.sub("{.*?}",'',license['href'])

        LOGGER.debug("Return at url %s", return_url)

        # id and name are not required by the LSD spec, but let's add them
        q = {"id": self.device_id, "name": self.device_name}
        r = requests.put(return_url, params=q)

        # check the return code vs the license status
        license_status = self.lsd['status']
        if r.status_code != requests.codes.ok:
            LOGGER.warning("Error structure: {}".format(r.text))
            if r.status_code == 403 and license_status in ["expired","returned","cancelled"]:
                LOGGER.info("The publication can't be returned, as the license is in state %s", 
                    license_status)    
                return
            elif r.status_code == 400 and license_status in ["ready", "revoked"]:
                LOGGER.info("The publication can't be returned properly, as the license is in state %s", 
                     license_status)    
                return
           
            # other cases are weird    
            raise TestSuiteRunningError(
                "Impossible to return the publication at {}: error {}; license status is {}".format(
                    return_url, r.status_code, license_status)
                )
        LOGGER.debug("The publication was successfully returned")   

        # if the return operation succeeds, 
        # the server MUST return an updated License Status Document
        try:
            self.lsd = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")

        # check that the status date has been updated
        self._check_datetime_updated('status', self.lsd['updated']['status'])

        # check the new status
        if (license_status == 'active' and self.lsd['status'] != 'returned') or \
           (license_status == 'ready' and self.lsd['status'] != 'cancelled'):
              raise TestSuiteRunningError(
                "The new status %s does not fit with the previous one {}".format(
                    license_status, self.lsd['status'])
                )
         
        return

    def initialize(self):
        """Initialize tests"""

        if not os.path.exists(self.license_path):
            raise TestSuiteRunningError(
                "License file {} not found".format(self.license_path))
        
        with open(self.license_path) as json_file:    
            self.lcpl = json.load(json_file)

        #todo: make them random
        self.device_id = 12345
        self.device_name = "EDRLab testing tools"


    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "fetch_lsd",
            "validate_lsd",
            "fetch_license",
            "register",
            "renew",
            "return"
            ]
