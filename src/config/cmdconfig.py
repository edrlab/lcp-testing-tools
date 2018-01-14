# -*- coding: utf-8 -*-

import yaml
import os

class CmdConfig:

  def __init__(self, config_path=None):
    if not config_path:
      config_path = os.environ.get('LCP_CMD_CONFIG')
    if not config_path:
      raise FileNotFoundError 

    if not os.path.exists(config_path):
        raise FileNotFoundError

    with open(config_path, 'r') as stream:
      yaml_config = yaml.load(stream)
      self.working_path = yaml_config['working_path']
      self.cmd = yaml_config['cmd']
      self.lcp_server = yaml_config['lcp_server']

    # cmd config
    self.encrypt_cmd_path = self.cmd['encrypt_cmd_path']
    self.encrypted_file_path = self.cmd['encrypted_file_path']
    self.user_passphrase_hint = self.cmd['user_passphrase_hint']
    self.user_passphrase = self.cmd['user_passphrase']
    # lcp_server config
    self.lcp_server_base_uri = self.lcp_server['base_uri']
    self.lcp_server_auth_user = self.lcp_server['auth']['user']
    self.lcp_server_auth_passwd = self.lcp_server['auth']['passwd']
    self.lcp_server_repository_path = self.lcp_server['repository_path']
    