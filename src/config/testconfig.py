import yaml
import json
import os
import sys

class TestConfig:

  PUBLICATION_MIMETYPE="application/epub+zip"
  STATUS_MIMETYPE="application/vnd.readium.license.status.v1.0+json"

  def __init__(self, test, config=None):
    if not config:
      config = os.environ.get('LCP_TEST_CONFIG')
    if not config:
      raise EnvironmentError 

    with open(config, 'r') as stream:
      yaml_config = yaml.load(stream)
      # raise error if 'test class name' is not in config
      self.test = yaml_config[test.__class__.__name__.lower()]
      self.common = yaml_config['common']

      # Parse all values here, to be used after in getters
      self.license_file = self.test['license']
      self.license_schema_file = self.common['license']['schema']
      self.crypto = self.common['crypto']['package']
      self.cacert_file = self.common['crypto']['cacert']


  def __str__(self):
    return str(self.raw)

  def __unicode(self):
    return unicode(self.raw)


  def raw_license(self):
    with open(self.license_file, 'r') as stream:
      return str(stream.read())

  def json_license(self):
    with open(self.license_file, 'r') as stream:
      return json.load(stream)  

  def json_license_schema(self):
    with open(self.license_schema_file, 'r') as stream:
      return json.load(stream)

  def crypto_package(self):
    sys.path.insert(0, self.crypto)
    return __import__('crypto')

  def cacert(self):
    return self.cacert_file

  def publication_mimetype(self):
    return self.PUBLICATION_MIMETYPE

  def status_mimetype(self):
    return self.STATUS_MIMETYPE

  def passphrase(self):
    return str(self.test['passphrase'])
