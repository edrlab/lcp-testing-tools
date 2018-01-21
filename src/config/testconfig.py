import yaml
import json
import os
import sys

class TestConfig:

  PUBLICATION_MIMETYPE="application/epub+zip"
  STATUS_MIMETYPE="application/vnd.readium.license.status.v1.0+json"

  def __init__(self, test=None, config=None):
    if not config:
      config = os.environ.get('LCP_TEST_CONFIG')
    if not config:
      raise EnvironmentError 

    with open(config, 'r') as stream:
      yaml_config = yaml.load(stream)
      # raise error if 'test class name' is not in config
      self.test = yaml_config[test] if test else None
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

  def publication_mimetype(self):
    return self.PUBLICATION_MIMETYPE

  def status_mimetype(self):
    return self.STATUS_MIMETYPE

  # Test specific config
  def license(self):
    return self.test['license']

  def passphrase(self):
    return str(self.test['passphrase'])

  def epub(self):
    return self.test['epub']
