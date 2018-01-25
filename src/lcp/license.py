import json
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import calendar
import codecs

from config.config import TestConfig

class License():

  LICENSE_MIMETYPE='application/vnd.readium.lcp.license.1.0+json'
  PUBLICATION_MIMETYPE="application/epub+zip"
  STATUS_MIMETYPE="application/vnd.readium.license.status.v1.0+json"

  def __init__(self, licensename, raw=False):
    self.config = TestConfig()
    if raw == False:
      with open(licensename, 'r') as license:
        self.license = json.load(license)
    else:
      if type(licensename) == 'byte':
        self.license = json.loads(licensename.decode('utf-8'))
      else:
        self.license = json.loads(licensename)

    self.rawlicense = json.dumps(self.license)

    with open(self.config.license_schema(), 'r') as schema:
      self.schema = json.load(schema)
      
    self.crypto = self.config.crypto_package()

 
  # All the useful getters
  def get_id(self):
    return self.license['id']

  def get_certificate(self):
    return self.license['signature']['certificate']

  def get_signature(self):
    return self.license['signature']['value']

  def get_link(self, name, param=None):
    for link in self.license['links']:
      if link['rel'] == name:
        return link[param] if param in link else link
    return None

  def get_issued(self):
    issued = self.license['issued']
    unix_time = calendar.timegm(dateparse(issued).timetuple())  
    return int(unix_time)

  def get_updated(self):
    updated = self.license['updated']
    unix_time = calendar.timegm(dateparse(updated).timetuple())  
    return int(unix_time)

  def get_user_key_hash_algo(self):
    return self.license['encryption']['user_key']['algorithm']

  def get_start(self):
    start = self.license['rights'].get('start', None) if 'rights' in self.license else None
    if not start:
      return None
    unix_time = calendar.timegm(dateparse(start).timetuple())  
    return int(unix_time)

  def get_end(self):
    end = self.license['rights'].get('end', None) if 'rights' in self.license else None
    if not end:
      return None
    unix_time = calendar.timegm(dateparse(end).timetuple())  
    return int(unix_time)

  def is_loan(self):
    return not self.get_end() is None 

  # get content key
  def get_content_key(self):
    return self.crypto.base64_decode(self.license['encryption']['content_key']['encrypted_value'])

  # compute canonical form 
  def get_canonical(self):
    return self.crypto.canonical(self.rawlicense)

  # check schema
  def check_schema(self):
    return jsonvalidate(self.license, self.schema)

  # def check user key
  def check_user_key(self, passphrase):
    user_key_hash_algo = self.license['encryption']['user_key']['algorithm']
    content_key_encryption_algo = self.license['encryption']['content_key']['algorithm']
    key_check = self.license['encryption']['user_key']['key_check']
    license_id = self.license['id']
    return self.crypto.check_userkey(passphrase, user_key_hash_algo,
                key_check, license_id, content_key_encryption_algo)

  def check_certificate(self):
    certificate = self.get_certificate()
    issued = self.get_issued()
    cacert = self.config.cacert()
    return self.crypto.verify_certificate(certificate, cacert, issued)

  def check_signature(self):
    certificate = self.get_certificate()
    signature = self.get_signature()
    canonical = self.get_canonical()
    return self.crypto.verify_sign_sha256(signature, certificate, canonical)

