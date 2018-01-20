import json
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time

from config.testconfig import TestConfig

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

  def __init__(self, status):
    self.config = TestConfig()
    self.status = json.loads(status)
    with open(self.config.status_schema(), 'r') as schema:
      self.schema = json.load(schema) 


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
    return self.status['status'] == READY
