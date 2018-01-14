# -*- coding: utf-8 -*-

"""
LCP license object
"""

import os
import sys
import logging
import json
import jsonschema
import base64
import datetime
import lcpcrypto
import dateutil.parser
import subprocess
from exception import LCPLicenseError

LOGGER = logging.getLogger(__name__)


class LCPLicense:

  def __init__(self):
    # in-memory license
    self.l = None
    # license path
    self.license_path = None
  
  def parse(self, license_path):
    self.license_path = license_path
    # unmarshall from a JSON string
    if not os.path.exists(license_path):
      raise LCPLicenseError(
          "License file {0} not found".format(self.license_path))

    with open(license_path, 'r', encoding='utf8') as json_file:    
      self.l = json.load(json_file)


  def validate(self, schema_path):
    # validate the license using the json schema
    # includes:
    #   check the profile Value (basic or 1.0)
    #   check the encryption method (aes-cbc), user key (sha256) and signature algorithm (ecdsa-sha256)

    with open(schema_path, 'r', encoding='utf8') as schema_file:
      lcpl_json_schema = json.load(schema_file)
      try:
          jsonschema.validate(self.l, lcpl_json_schema, format_checker=jsonschema.FormatChecker())
      except jsonschema.ValidationError as err:
          raise LCPLicenseError(err)


  def hint_link(self):
    # returns a link to the hint page
    for lk in self.l['links']:
        if lk['rel'] == 'hint':
          return lk['href']
            
  def publication_link(self):
    # returns a link to the publication resource
    for lk in self.l['links']:
        if lk['rel'] == 'publication':
          return lk['href']
            
  def status_link(self):
    # returns a link to the status document
    for lk in self.l['links']:
        if lk['rel'] == 'status':
          return lk['href']


  def check_required_links(self):
    # check the presence of rel="hint"" and "publication"" links, required by the specification.
    # check the mime-type of a publication link.
    # such constraints appear un-checkable with a json schema.
    res = 0
    for lk in self.l['links']:
        if lk['rel'] == 'hint':
            res +=1
        if lk['rel'] == 'publication':
            if lk['type'] != None and lk['type'] != "application/epub+zip":
                raise LCPLicenseError(
                    "A 'publication' link must have an 'application/epub+zip' type")              
            res +=1
        if lk['rel'] == 'status':
            if lk['type'] != None and lk['type'] != "application/vnd.readium.license.status.v1.0+json":
                raise LCPLicenseError(
                    "A 'status' link must have an 'application/vnd.readium.license.status.v1.0+json' type")
            res +=1
    if res != 3:
        raise LCPLicenseError(
            "Missing required 'hint', 'publication' or 'status' link in the license file")
        
  def check_content_key(self):
    # check the format of content key (64 bytes)
    encrypted_value = self.l['encryption']['content_key']['encrypted_value']
    value_len = len(base64.b64decode(encrypted_value))
    #LOGGER.debug("data {}".format(base64.b64decode(encrypted_value)))
    if value_len != 64:
        raise LCPLicenseError("encrypted value is {} bytes long".format(value_len))

  def check_key_check(self, passphrase):
    # check the key_check value (base64 decoded key_check value = cleartext id value)
    # cf 2.1.4.5
    # cat license.lcpl | jq -r .encryption.user_key.key_check | openssl enc -d -base64 -A | wc -c
    # to compare with $(cat license.lcpl | jq -r .id | wc -c) + 28
    
    # key_check: The value of the License Document `id` field, encrypted using the User Key and the same algorithm identified for Content Key 
    # encryption in `encryption/content_key/algorithm`. This is used to verify that the Reading System has the correct User Key.

    key_check = self.l['encryption']['user_key']['key_check']
    key_check_bytes = base64.b64decode(key_check)
    if len(key_check_bytes) != 64:
        raise LCPLicenseError("key check is {} bytes long".format(len(key_check_bytes) ))

    hash_algorithm = self.l['encryption']['user_key']['algorithm']

    passphrase_hash = lcpcrypto.hash(passphrase, hash_algorithm)
    if passphrase_hash == None:
        raise LCPLicenseError("error hashing the passphrase")

    decrypt_algorithm = self.l['encryption']['content_key']['algorithm']
    clear_value = lcpcrypto.decrypt(key_check_bytes, passphrase_hash, decrypt_algorithm)
    if clear_value == None:
        raise LCPLicenseError("error decrypting the key check value")

    license_id = self.l['id']
    if clear_value != license_id:
        raise LCPLicenseError("decrypted key check {} different from id {} ".format(clear_value, license_id))            
    pass

  def check_signature(self, cert_path):
    # check the signature value using the java signature tool
    # this java code returns 1+ if the signature is not valid 
    if not os.path.exists(cert_path):
        raise LCPLicenseError(
            "Root certificate file {0} not found".format(cert_path))
        
    run_script = '../SignatureVerifier_Java/run-from-py.sh' if os.name == 'posix' else '../SignatureVerifier_Java/run-from-py.bat'
    run_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), run_script)
        
    # if a verbose signature check is needed for debug, add "verbose" as a last arg
    args = [run_path, cert_path, self.license_path]

    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    if r.returncode > 0:
        LOGGER.error("return code is {}".format(r.returncode))
        raise LCPLicenseError(r.stdout.strip())

    LOGGER.debug(r.stdout.strip())

  def rights_copy(self):
    # returns the number of characters which can be copied, as an integer 
    # sys.maxsize is the largest int we can imagine.
    rights = self.l['rights']
    if 'copy' in rights:
      LOGGER.info("copy : {}".format(rights['copy']))
      return int(rights['copy'])
    else:
      return sys.maxsize

  def rights_print(self):
    # returns the number of pages which can be printed, as an integer 
    rights = self.l['rights']
    if 'print' in rights:
      LOGGER.info("print : {}".format(rights['print']))
      return int(rights['print'])
    else:
      return sys.maxsize

  def rights_start(self):
    rights = self.l['rights']
    if 'start' in rights:
      LOGGER.info("start: {}".format(rights['start']))
      return dateutil.parser.parse(rights['start'])
    else:
      return None

  def rights_end(self):
    rights = self.l['rights']
    if 'end' in rights:
      LOGGER.info("end: {}".format(rights['end']))
      return dateutil.parser.parse(rights['end'])
    else:
      return None

  def check_dates(self):
    # check the datetime rights expressed in the license
    now = datetime.datetime.now(datetime.timezone.utc)
    start = self.rights_start()
    end   = self.rights_end()
    if start and now < start:
      LOGGER.info("The start date has not been reached")
      return False
    if end and now > end:
      LOGGER.info("The license has expired")
      return False
    else:
      return True



