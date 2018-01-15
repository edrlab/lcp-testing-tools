# -*- coding: utf-8 -*-

"""
Check the features of a License Document Server.

History
    Created By Cyrille Lebeaupin / EDRLab, 2017
    Includes code from Ahram Oh / DRM Inside, 2016
    Updated by Laurent Le Meur / EDRLab, 2017 

Copyright 2017 European Digital Reading Lab. All rights reserved.
Licensed to the Readium Foundation under one or more contributor license agreements.
Use of this source code is governed by a BSD-style license
that can be found in the LICENSE file exposed on Github (readium) in the project repository.
"""

import json
import logging
import os.path
import datetime, time
import dateutil.parser
import requests
import jsonschema
import re
from exception import TestSuiteRunningError
from base_test_suite import BaseTestSuite

LOGGER = logging.getLogger(__name__)

DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"



class LSDTestSuite(BaseTestSuite):
    """LSD test suite"""

    def __init__(self, config, license_path):
        """
        Args:
            config (TestConfig): Configuration object
            license_path (str): Path to an lcpl file
        """

        self.config = config
        self.license_path = license_path

        # LCP License
        self.lcpl = None

        # License Status Document
        self.lsd = None

        # test device id and name
        self.device_id = 0
        self.device_name = ""

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
        LOGGER.info("The {} was last updated on: {}".format(field, date_time) )  
        status_datetime = dateutil.parser.parse(date_time)
        td = datetime.timedelta(minutes=1)
        if status_datetime + td < datetime.datetime.now(datetime.timezone.utc):
            LOGGER.warning("It seems that the timestamp was not updated!") 


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
        #LOGGER.debug(self.lsd)   

    def test_validate_lsd(self):
        """
        Validate a License Status Document
        """

        with open(self.config.status_schema_path) as schema_file:
            lsd_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lsd, lsd_json_schema, format_checker=jsonschema.FormatChecker())
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

        LOGGER.debug("The License Status Document is valid")   

        # these are required properties -> if absent, has been spotted by the schema validation
        LOGGER.info("The status of the license is: %s", self.lsd['status'])  
        LOGGER.info("The user message is: %s", self.lsd['message'])   
        
        if 'potential_rights' in self.lsd:
            LOGGER.info("The potential rights datetime is: %s", self.lsd['potential_rights']['end'])   
        else:
            LOGGER.info("No potential rights datetime in the status document")  
        if 'events' in self.lsd:
            for event in self.lsd['events']:
                LOGGER.info("Event: type {}, timestamp {}, id {}, name {}".format(
                    event['type'], 
                    event['timestamp'],
                    event['id'],
                    event['name'])
                )   
        else:
            LOGGER.info("No events in the status document")  

    def test_required_links(self):
        """ Check the presence of the required links
        check the presence of a rel="license"" link, required by the specification.
        check the presence of a rel="register" link, required by EDRLab.
        check the mime-type of the different links (including renew and return links).
        such constraints appear un-checkable with a json schema.
        """
        res = 0
        renew_link = False
        return_link = False
        for l in self.lsd['links']:
            if l['rel'] == 'license':
                res +=1
                if l['type'] != None and l['type'] != "application/vnd.readium.lcp.license-1.0+json":
                    LOGGER.info("license link has type {}".format(l['type'])) 
                    raise TestSuiteRunningError(
                        "A 'license' link must have an 'application/vnd.readium.lcp.license-1.0+json' type")              

            if l['rel'] == 'register':
                res +=1 
                if l['type'] != None and l['type'] != "application/vnd.readium.license.status.v1.0+json":
                    raise TestSuiteRunningError(
                        "A 'register' link must have an 'application/vnd.readium.license.status.v1.0+json' type")            
                if not 'templated' in l or l['templated'] != True:
                    raise TestSuiteRunningError(
                        "A 'register' link must be templated (id and name)")            

            if l['rel'] == 'renew' :
                renew_link = True
                if l['type'] != None and l['type'] != "application/vnd.readium.license.status.v1.0+json":
                    raise TestSuiteRunningError(
                        "A 'renew' link must have an 'application/vnd.readium.license.status.v1.0+json' type")
                if not 'templated' in l or l['templated'] != True:
                    raise TestSuiteRunningError(
                        "A 'renew' link must be templated (end, id and name)")            

            if l['rel'] == 'return' :
                return_link = True
                if l['type'] != None and l['type'] != "application/vnd.readium.license.status.v1.0+json":
                    raise TestSuiteRunningError(
                        "A 'return' link must have an 'application/vnd.readium.license.status.v1.0+json' type")
                if not 'templated' in l or l['templated'] != True:
                    raise TestSuiteRunningError(
                        "A 'return' link must be templated (id and name)")            
        
        if renew_link == False:
            LOGGER.info("No renew link in the status document") 
        if return_link == False: 
            LOGGER.info("No return link in the status document")  

        if res != 2:
            raise TestSuiteRunningError(
                "Missing required 'license' or 'register' link in the license file")
           
        pass
                

    def test_fetch_license(self):
        """ Fetch a license from the URL found in the status doc """

        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'license'))
        except StopIteration as err:
            raise TestSuiteRunningError(
                "Missing a 'license' link in the status document")
        
        license_url = license['href']
        LOGGER.debug("Fetch license at url %s:", license_url)   

        # fetch the license
        try:
            r = requests.get(license_url)
            if r.status_code != requests.codes.ok:
                raise TestSuiteRunningError(
                    "Impossible to fetch the License  at {}: error {}".format(
                        license_url, r.status_code)
                    )
        except requests.exceptions.RequestException as err:
            raise TestSuiteRunningError(err)

        # parse the license
        try:
            self.lcpl = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Document")
        LOGGER.debug("The License is available")   

    def test_rights(self):
        # check the rights expressed in the license
        rights = self.lcpl['rights']
        now = datetime.datetime.now(datetime.timezone.utc)
        if 'start' in rights:
            LOGGER.info("start: {}".format(rights['start']))
            if now <  dateutil.parser.parse(rights['start']):
                LOGGER.info("The start date is not reached")
        if 'end' in rights:
            LOGGER.info("end  : {}".format(rights['end']))
            if now > dateutil.parser.parse(rights['end']):
                LOGGER.info("The license has expired")
        if 'copy' in rights:
            LOGGER.info("copy : {}".format(rights['copy']))
        if 'print' in rights:
            LOGGER.info("print: {}".format(rights['print']))


    def test_validate_license(self):
        """ Validate the newly fetched license """

        with open(self.config.license_schema_path) as schema_file:
            lcpl_json_schema = json.loads(schema_file.read())
            try:
                jsonschema.validate(self.lcpl, lcpl_json_schema, format_checker=jsonschema.FormatChecker())
            except jsonschema.ValidationError as err:
                raise TestSuiteRunningError(err)

        LOGGER.debug("The up to date License is available and valid")


    def _register_device(self, noname):
        """
        Register a device for the current license

        Args:
            noname: boolean, True if we try to register with no id nor name

        Return:
            boolean, success or error
        """
        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'register'))
        except StopIteration as err:
            LOGGER.warning("'register' link missing in the status document")
            return False

        # removes the 'blank' part in the templated URL
        register_url = re.sub("{.*?}",'',license['href'])

        LOGGER.debug("Register at url %s", register_url)

        # if we want to check that a register with no id and name fails
        if noname:
            r = requests.post(register_url)
        else:
            # id and name are required in the LSD spec
            q = {"id": self.device_id, "name": self.device_name}
            # register the device for the current license
            r = requests.post(register_url, params=q)

        # check the return code vs the license status
        if r.status_code != requests.codes.ok:
            LOGGER.warning("Error registering: {}".format(r.text))
            # error 400 is in the lsd spec, 403 should be added
            if r.status_code in [400, 403]:
                if self.lsd['status'] in ["expired", "returned","cancelled","revoked"]:
                    LOGGER.info("The device could not be registered because the license was {}".format(self.lsd['status']))
                elif self.lsd['status'] == "active" and noname==False:
                    LOGGER.info("The device was certainly already registered before")                 
                return False
            # other cases are weird    
            raise TestSuiteRunningError(
                "Impossible to register the device at {}: error {}".format(
                    register_url, r.status_code)
                )
        # if the register operation succeeds, 
        # the server MUST return an updated License Status Document
        try:
            self.lsd = r.json()            
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")
        return True

    def test_register(self):
        """ Register a device for the current license.
            Check there is no error in case of multiple registering
            Check the error is registering is not possible.
        """
        if self._register_device(noname=False):
            LOGGER.debug("The device was successfully registered")   

            # check the the new lsd structure is valid
            self.test_validate_lsd()

            # check that the status date has been updated
            LOGGER.info("The current datetime is {}".format(datetime.datetime.utcnow().strftime(DEFAULT_DATETIME_FORMAT)))   
            self._check_datetime_updated('status', self.lsd['updated']['status'])
        else:
            raise TestSuiteRunningError("The device wasn't successfully registered")

    def test_register_noname(self):
        """ Register a device for the current license wih no id nor name.
            The server should return an error
        """
        if self._register_device(noname=True):
            raise TestSuiteRunningError("The server must not accept registering with no id and name")

    def test_register_twice(self):
        """ Register for the second time a device for the current license.
            The server should not return an error
        """
        if self._register_device(noname=False):
            LOGGER.info("The server accepts double registrations")

    def _renew_license(self, renew_days):
        """
        Renew the current license

        Args:
            renting_days: number of additional days

        Return:
            boolean, success or error
        """
        try:
            license = next((l for l in self.lsd['links'] if l['rel'] == 'renew'))
        except StopIteration as err:
            LOGGER.warning("No 'renew' link in the status document. ok if buy")
            return False

        # removes the 'blank' part in the templated URL
        renew_url = re.sub("{.*?}",'',license['href'])

        LOGGER.debug("Renew at url %s", renew_url)
        LOGGER.debug("Current end date: {}".format(self.lcpl['rights']['end']))
        if 'potential_rights' in self.lsd:
            LOGGER.debug("Max end date: %s", self.lsd['potential_rights']['end'])   
            if dateutil.parser.parse(self.lcpl['rights']['end']) == \
                dateutil.parser.parse(self.lsd['potential_rights']['end']):
                LOGGER.info("Max end date reached, impossible to renew")   
                return False    
        else:
            LOGGER.info("No max end date indicated")   

        # let's renew for N days after the current end date
        license_end = dateutil.parser.parse(self.lcpl['rights']['end']) + datetime.timedelta(days=renew_days)

        end = license_end.strftime(DEFAULT_DATETIME_FORMAT)
       
        LOGGER.info("Renew until {}".format(end))   

        # id and name are not required by the LSD spec, but let's add them
        q = {"id": self.device_id, "name": self.device_name, "end": end}
        r = requests.put(renew_url, params=q)

        # check the return code vs the license status
        license_status = self.lsd['status']
        if r.status_code != requests.codes.ok:
            LOGGER.warning("Error structure: {}".format(r.text))
            if r.status_code in [400, 403] and license_status != "active":                
                LOGGER.info("The publication can't be renewed properly, as the license is {}".format(license_status))  
                return False
           
            # other cases are weird    
            raise TestSuiteRunningError(
                "Impossible to renew the publication at {}: error {}; license status is {}".format(
                    renew_url, r.status_code, license_status)
                )

        # if the renew operation succeeds, 
        # the server MUST return an updated License Status Document         
        try:
            self.lsd = r.json()         
        except ValueError as err:
            LOGGER.debug(r.text)
            raise TestSuiteRunningError("Malformed JSON License Status Document")
        return True


    def test_renew(self):
        """ Renew a license if renewable.
            Check the error if the license is not (or not anymmore) renewable.
        """
        LOGGER.info("now is {}".format(datetime.datetime.utcnow().strftime(DEFAULT_DATETIME_FORMAT)))   
        LOGGER.info("The current status updated datetime is {}".format(self.lsd['updated']['status']))

        if self._renew_license(renew_days=2):
            LOGGER.debug("The publication was successfully renewed for 2 days")   

            # check the the new lsd structure is valid
            self.test_validate_lsd()

            # check that the status timestamp has been updated
            self._check_datetime_updated('status', self.lsd['updated']['status'])
            # check that the license timestamp has been updated
            self._check_datetime_updated('license', self.lsd['updated']['license'])
            # check the new status
            if (self.lsd['status'] != 'active') :
                raise TestSuiteRunningError(
                    "The new status {} does not fit: must be active".format(self.lsd['status'])
                    )
            # sleep -> let the server update the license
            #time.sleep(2)
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
            if r.status_code in [400, 403] and license_status != "active":    
                LOGGER.info("The publication can't be returned properly, as the license is {}".format(license_status))  
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

        # check the the new lsd structure is valid
        self.test_validate_lsd()

        # check that the status timestamp has been updated
        LOGGER.info("The current datetime is {}".format(datetime.datetime.utcnow().strftime(DEFAULT_DATETIME_FORMAT)))   
        self._check_datetime_updated('status', self.lsd['updated']['status'])
        # check that the license timestamp has been updated
        # (the end date has been updated in the license)
        self._check_datetime_updated('license', self.lsd['updated']['license'])

        # check the new status
        if (license_status == 'active' and self.lsd['status'] != 'returned') or \
           (license_status == 'ready' and self.lsd['status'] != 'cancelled'):
              raise TestSuiteRunningError(
                "The new status {} does not fit with the previous one {}".format(
                    license_status, self.lsd['status'])
                )
         
        return

    def get_tests(self):
        """
        Names of tests to run
        """

        return [
            "fetch_lsd",
            "validate_lsd",
            "required_links",
            "fetch_license",
            "rights",
            "validate_license",
            "register_noname",
            "register",
            "register_twice",
            "renew",
            "fetch_license",
            "rights",
            "return",
            "fetch_license",
            "rights"
            ]
