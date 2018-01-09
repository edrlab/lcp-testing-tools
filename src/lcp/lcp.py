import json
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time

from config.testconfig import TestConfig

class License():
  def __init__(self, licensename, schemaname):
    with open(licensename, 'r') as license, open(schemaname, 'r') as schema:
      self.license = json.load(license)
      self.schema = json.load(schema)
      license.seek(0)
      self.rawlicense = str(license.read())
      self.config = TestConfig()
      self.crypto = self.config.crypto_package()
 
  # All the useful getters
  def get_id(self):
    return str(self.license['id'])

  def get_certificate(self):
    return str(self.license['signature']['certificate'])

  def get_signature(self):
    return str(self.license['signature']['value'])

  def get_link(self, name, param=None):
    for link in self.license['links']:
      if link['rel'] == name:
        return link[param] if param in link else link
    return None

  def get_issued(self):
    issued = self.license['issued']
    unix_time = time.mktime(dateparse(issued).timetuple())  
    return int(unix_time)

  def get_updated(self):
    updated = self.license['updated']
    unix_time = time.mktime(dateparse(updated).timetuple())  
    return int(unix_time)

  def get_user_key_hash_algo(self):
    return str(self.license['encryption']['user_key']['algorithm'])

  def get_start(self):
    start = self.license['rights'].get('start')
    if not start:
      return None
    unix_time = time.mktime(dateparse(start).timetuple())  
    return int(unix_time)

  def get_end(self):
    end = self.license['rights'].get('end')
    if not end:
      return None
    unix_time = time.mktime(dateparse(end).timetuple())  
    return int(unix_time)

  # get content key
  def get_content_key(self):
    return self.crypto.base64_decode(str(self.license['encryption']['content_key']['encrypted_value']))

  # compute canonical form 
  def get_canonical(self):
    return self.crypto.canonical(self.rawlicense)

  # check schema
  def check_schema(self):
    return jsonvalidate(self.license, self.schema)

  # def check user key
  def check_user_key(self, passphrase):
    user_key_hash_algo = str(self.license['encryption']['user_key']['algorithm'])
    content_key_encryption_algo = str(self.license['encryption']['content_key']['algorithm'])
    key_check = str(self.license['encryption']['user_key']['key_check'])
    license_id = str(self.license['id'])
    return self.crypto.check_userkey(passphrase, user_key_hash_algo,
                key_check, license_id, content_key_encryption_algo)

