# -*- coding: utf-8 -*-

"""
Test suite config handler 
"""

import yaml
import os
import sys

class TestConfig:

  PUBLICATION_MIMETYPE="application/epub+zip"
  LICENSE_MIMETYPE = "application/vnd.readium.lcp.license-1.0+json"
  STATUS_MIMETYPE="application/vnd.readium.license.status.v1.0+json"

  def __init__(self, config_path=None, test=None):
    if not config_path:
        config_path = os.environ.get('LCP_TST_CONFIG')
    if not config_path:
        raise FileNotFoundError 

    if not os.path.exists(config_path):
        raise FileNotFoundError

    with open(config_path, 'r') as stream:
        yaml_config = yaml.load(stream)
        self.working_path = yaml_config['working_path']
        self.cmd = yaml_config['cmd']
        self.common = yaml_config['common']
        self.lcp_server = yaml_config['lcp_server']
        self.lsd_server = yaml_config['lsd_server']
        self.test = yaml_config[test] if test else None

    # cmd config
    self.user_passphrase = self.cmd['user_passphrase']
    # common config
    self.encryption_schema = self.common['schema']['encryption']
    self.license_schema_path = self.common['schema']['license']
    self.status_schema_path= self.common['schema']['status']
    self.cacert = self.common['crypto']['cacert']
    # lcp_server config
    self.lcp_server_base_uri = self.lcp_server['base_uri']
    self.lcp_server_auth_user = self.lcp_server['auth']['user']
    self.lcp_server_auth_passwd = self.lcp_server['auth']['passwd']
    self.lcp_server_repository_path = self.lcp_server['repository_path']
    # lsd_server config
    self.lsd_server_base_uri = self.lsd_server['base_uri']
    self.lsd_server_auth_user = self.lsd_server['auth']['user']
    self.lsd_server_auth_passwd = self.lsd_server['auth']['passwd']
    # test x.y config
    if self.test:
        self.test_epub = self.test['epub']
        self.test_license = self.test['license']
        self.test_passphrase = self.test['passphrase']
  
  # dynamically load the C crypto package via its python wrapper
  def crypto_package(self):
    sys.path.insert(0, self.common['crypto']['package'])
    return __import__('crypto')

