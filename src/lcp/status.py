import json
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time
import urllib
from uritemplate import expand

from config.testconfig import TestConfig
from .license import License

class Status():

  READY = 'ready'
  ACTIVE = 'active'
  REVOKED = 'revoked'
  RETURNED = 'returned'
  CANCELLED = 'cancelled'
  EXPIRED = 'expired'

  REGISTER = 'register'
  CANCEL = 'cancel'
  REVOKE = 'revoke'
  RENEW = 'renew'
  RETURN = 'return'

  DEVICEID1 = '6f2bd94-3dcf-4034-a663-5f2a7945ee52'
  DEVICENAME1 = 'My reading device 1'

  def __init__(self, license):
    self.config = TestConfig()
    self.link = license.get_link('status', 'href')
    with open(self.config.status_schema(), 'r') as schema:
      self.schema = json.load(schema) 

  def _download(self, link):
    response = urllib.urlopen(link)
    if response.getcode() == 200:
      return response.read()
    else:
      raise IOError('Register return HTTP error {}'.format(response.getcode()))

  def update_status(self):
    self.status = json.loads(self._download(self.link))

  def update_license(self):
    licenselink = self.get_link('license', 'href')
    return License(self._download(licenselink), raw=True)

  def check_schema(self):
    return jsonvalidate(self.status, self.schema)

  def get_events(self):
    return self.status.get('events', None) 

  def get_link(self, name, param=None):
    for link in self.status['links']:
      if link['rel'] == name:
        return link[param] if param in link else link
    return None

  def is_ready(self):
    return self.status['status'] == self.READY

  def is_active(self):
    return self.status['status'] == self.ACTIVE

  def register(self, deviceid, devicename):
    link = self.get_link(self.REGISTER)
    if link['templated']:
      regurl = expand(link['href'], {'id': deviceid, 'name':devicename})
      self.status = json.loads(self._download(regurl))
    else:
      self.status = json.loads(link['href'])


