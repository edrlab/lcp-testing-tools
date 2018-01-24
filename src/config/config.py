import yaml
import json
import os
import sys

class TestConfig:

  def __init__(self, data=None, config=None):
    if not config:
      config = os.environ.get('LCP_TEST_CONFIG')
    if not config:
      raise EnvironmentError 

    with open(config, 'r') as stream:
      yaml_config = yaml.load(stream)
      self.data = yaml_config['data'][data] if data else None
      self.common = yaml_config['common']

  # Common config for all tests
  def provider(self):
    return self.common['provider']

  def license_schema(self):
    return self.common['license']['schema']

  def encryption_schema(self):
    return self.common['encryption']['schema']

  def status_schema(self):
    return self.common['status']['schema']

  def cacert(self):
    return str(self.common['crypto']['cacert'])

  def crypto_package(self):
    sys.path.insert(0, self.common['crypto']['package'])
    return __import__('crypto')

  # Data specific config
  def license(self):
    return self.data['license']

  def passphrase(self):
    return str(self.data['passphrase'])

  def epub(self):
    return self.data['epub']
