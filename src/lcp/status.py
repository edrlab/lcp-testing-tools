import json
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import calendar
from datetime import datetime
import requests
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

  def _get(self, link):
    r = requests.get(link)
    if r.status_code == 200:
      return r.text
    else:
      raise IOError('GET {} HTTP error {}'.format(link, r.status_code))

  def _post(self, link):
    r = requests.post(link)
    if r.status_code == 200:
      return r.text
    else:
      raise IOError('POST {} HTTP error {}'.format(link, r.status_code))

  def _put(self, link):
    r = requests.put(link)
    if r.status_code == 200:
      return r.text
    else:
      raise IOError('PUT {} HTTP error {}'.format(link, r.status_code))


  def update_status(self):
    self.status = json.loads(self._get(self.link))

  def update_license(self):
    licenselink = self.get_link('license', 'href')
    return License(self._get(licenselink), raw=True)

  def check_schema(self):
    return jsonvalidate(self.status, self.schema)

  def get_events(self):
    return self.status.get('events', None) 

  def get_link(self, name, param=None):
    for link in self.status['links']:
      if link['rel'] == name:
        return link[param] if param in link else link
    return None

  def get_updated_status(self):
    updated = self.status['updated']['status']
    unix_time = calendar.timegm(dateparse(updated).timetuple())  
    return int(unix_time)

  def is_ready(self):
    return self.status['status'] == self.READY

  def is_active(self):
    return self.status['status'] == self.ACTIVE

  def is_cancelled(self):
    return self.status['status'] == self.CANCELLED

  def is_revoked(self):
    return self.status['status'] == self.REVOKED

  def register(self, deviceid, devicename):
    link = self.get_link(self.REGISTER)
    if link['templated']:
      regurl = expand(link['href'], {'id': deviceid, 'name':devicename})
      self.status = json.loads(self._post(regurl))
    else:
      self.status = json.loads(self._post(link['href']))

  def renew(self, deviceid, devicename, end):
    link = self.get_link(self.RENEW)
    try:
      pend = datetime.utcfromtimestamp(end).isoformat()+'Z'
    except:
      pend = end

    if link['type'] == License.STATUS_MIMETYPE and link['templated'] == True:
      regurl = expand(link['href'], {'id': deviceid, 'name':devicename, 'end':pend})
      self.status = json.loads(self._put(regurl))

  def renewnoend(self, deviceid, devicename):
    link = self.get_link(self.RENEW)
    if link['type'] == License.STATUS_MIMETYPE and link['templated'] == True:
      regurl = expand(link['href'], {'id': deviceid, 'name':devicename})
      self.status = json.loads(self._put(regurl))

  def renewnodevice(self, end):
    link = self.get_link(self.RENEW)
    pend = datetime.utcfromtimestamp(end).isoformat()+'Z'
    if link['type'] == License.STATUS_MIMETYPE and link['templated'] == True:
      regurl = expand(link['href'], {'end':pend})
      self.status = json.loads(self._put(regurl))
