# -*- coding: utf-8 -*-

"""
Config handlers
"""

import os.path
from base64 import b64encode

import yaml

from exception import ConfigParseError

class BasicServerConfig:
    """Classic server config"""

    def __init__(self, yaml_prefix, config):
        """

        Args:
            yaml_prefix (string): Yaml prefix in the configuration file
            config (dict): Config dictionnary
        """

        self.yaml_prefix = yaml_prefix
        self.base_uri = None
        self.auth_digest = None

        # Build config
        self.load_config(config)

    def load_config(self, config):
        """
        Load config file

        Args:
            config (dict): Config dictionnary
        """

        # Get base uri
        try:
            self.base_uri = config['base_uri']
        except KeyError:
            raise ConfigParseError(
                "config: {0}.base_uri not defined".format(self.yaml_prefix))

        if 'auth' not in config:
            return

        # Process authentication
        try:
            user = config['auth']['user']
        except KeyError:
            raise ConfigParseError(
                "config: {0}.auth.user not defined".format(
                    self.yaml_prefix))

        try:
            passwd = config['auth']['passwd']
        except KeyError:
            raise ConfigParseError(
                "config: {0}.auth.passwd not defined".format(
                    self.yaml_prefix))

        self.auth_digest = b64encode(
            bytes(user + ":" + passwd, "utf-8")).decode("ascii")


class LcpServerConfig(BasicServerConfig):
    """Config for LCP server"""

    def __init__(self, yaml_prefix, config):
        """

        Args:
            yaml_prefix (string): Yaml prefix in configuration file
            config (dict): Config dictionnary
        """

        super(LcpServerConfig, self).__init__(yaml_prefix, config)
        self.yaml_prefix = yaml_prefix
        self.external_repository_path = None
        self.internal_repository_path = None
        self.user_passphrase_hint = None
        self.user_passphrase = None

        # Build config
        self.load_config(config)

    def load_config(self, config):
        """
        Load config file

        Args:
            config (dict): Config dictionnary
        """

        super(LcpServerConfig, self).load_config(config)

        # Get lcp server external repository path
        try:
            self.external_repository_path = \
                config['external_repository_path']
        except KeyError:
            raise ConfigParseError(
                "config: {0}.external_repository_path not defined".format(
                    self.yaml_prefix))

        if not os.path.exists(self.external_repository_path):
            raise ConfigParseError(
                "config: {0}.external_repository_path does not exist".format(
                    self.yaml_prefix))

        # Get lcp server internal repository path
        try:
            self.internal_repository_path = \
                config['internal_repository_path']
        except KeyError:
            raise ConfigParseError(
                "config: {0}.internal_repository_path not defined".format(
                    self.yaml_prefix))

        if 'user_passphrase_hint' in config:
            self.user_passphrase_hint = config['user_passphrase_hint']
        else:
            self.user_passphrase_hint = "Enter your passphrase"

        if 'user_passphrase' in config:
            self.user_passphrase = config['user_passphrase']
        else:
            self.user_passphrase = str(uuid.uuid4())


class ConfigManager:
    """Config manager"""

    def __init__(self, config_path):
        """
        Initialize config manager

        Args:
            config_path (str): Path to the configuration file
        """

        # LCP encrypt parameters
        self.lcp_encrypt_cmd_path = None

        # LCP server
        self.lcp_server = None

        # LSD server
        self.lsd_server = None

        # LCPL and publication files are stored in this directory
        self.working_path = None

        # Root certificate path
        self.root_cert_path = None

        # Process config file
        self.load_config_file(config_path)

    def load_config_file(self, config_path):
        """
        Parse and load configuration file

        Args:
            config_path: Path of configuration file
        """

        if not os.path.exists(config_path):
            raise ConfigParseError(
                "Config file does not exist"
            )

        with open(config_path, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as err:
                raise ConfigParseError("config: {0}", err)

        self.load_config(config)

    def load_config(self, config):
        """
        Load config file

        Args:
            config (dict): Config dictionnary
        """

        # Get working_path
        try:
            self.working_path = config['working_path']
        except KeyError:
            raise ConfigParseError(
                "config: working_path not defined")

        # Get lcpencrypt command path
        try:
            self.lcp_encrypt_cmd_path = config['lcp_encrypt']['cmd_path']
        except KeyError:
            raise ConfigParseError(
                "config: lcp_encrypt/cmd_path not defined")

        if not os.path.exists(self.lcp_encrypt_cmd_path):
            raise ConfigParseError(
                "config: the lcp encrypt cmd path does not exist")

        # Parse lcp server config
        if 'lcp_server' in config:
            self.lcp_server = LcpServerConfig(
                "lcp_server", config['lcp_server'])

        # Parse lsd server config
        if 'lsd_server' in config:
            self.lsd_server = BasicServerConfig(
                "lsd_server", config['lsd_server'])

        # Get root_cert_path
        try:
            self.root_cert_path = config['root_cert_path']
        except KeyError:
            raise ConfigParseError(
                "config: root_cert_path not defined")
