# -*- coding: utf-8 -*-

"""
Interactive command interface for the open-source LCP Server

Copyright EDRLab, 2017

Protect an epub file using a locally install Encryption utility and a remote License Server;
Retrieve a license;
Retrieve an LCP Protected publication from the server.

Note: The License Server must be running when the utility is started, if interaction with this server is planned.
"""

import sys
import argparse
import datetime
import hashlib
import json
import os.path
import uuid
import shutil
import requests
from urllib.parse import urljoin
import util
from cmd import Cmd
from config.cmdconfig import CmdConfig

W3C_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"

class LCPCmdShell(Cmd):
    intro = 'Welcome to the LCP cmd shell.   Type help or ? to list commands.\n'
    prompt = '(lcp) '

    def __init__(self, config, epub_path):
        """
        Args:
            config_manager (ConfigManager): ConfigManager object
            epub_path (str): Path to an epub file
        """
        super(LCPCmdShell, self).__init__()

        self.config= config
        self.epub_path = epub_path

        filename, file_extension = os.path.splitext(os.path.basename(epub_path))
        self.epub_filename = filename

        # Protected content information
        self.encrypted_content_id = None
        self.encrypted_content_encryption_key = None
        self.encrypted_content_filename = None
        self.encrypted_content_location = None
        self.encrypted_content_length= None
        self.encrypted_content_sha256 = None

        # To be used by subsequent actions
        self.license_path = None
        self.protected_file_path = None


    def __printLCPServerErrorMsg(self, r):
        """ print the error msg returned from the LCP server, 
            formatted in JSON.
            The parameter is a requests response
        """
        error = r.json()
        print ("{} ({}): {}".format(error['title'], error['status'], error['detail']))

    def __build_partial_license(self):
        """Build partial license

        Returns:
            dict
        """

        license_print = 2
        license_copy = 100
        # 100 days to read the publication
        license_start_datetime = datetime.datetime.today()
        license_end_datetime = license_start_datetime + \
            datetime.timedelta(days=100)

        # Random provider id, in the form of a uri
        provider_id = "http://{}.com".format(str(uuid.uuid4()))
        # Random user id and email
        user_id = str(uuid.uuid4())
        user_email = "{}@lcp.edrlab.org".format(user_id)

        # Hash the passphrase (found in the config)
        hash_engine = hashlib.sha256()
        hash_engine.update(self.config.user_passphrase.encode("utf-8"))
        user_hashed_passphrase = hash_engine.hexdigest()

        # Prepare a partial license
        partial_license = {
            "provider": provider_id,
            "user": {
                "id": user_id,
                "email": user_email,
                "encrypted": ["email"]
            },
            "encryption": {
                "user_key": {
                    "text_hint": self.config.user_passphrase_hint,
                    "value": user_hashed_passphrase,
                    "algorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
                    }
            },
            "rights": {
                "print": license_print,
                "copy": license_copy,
                "start": license_start_datetime.strftime(W3C_DATETIME_FORMAT),
                "end": license_end_datetime.strftime(W3C_DATETIME_FORMAT)
            }
        }

        return partial_license


    def do_encrypt(self, args):
        """
        Encrypt an epub file using the *local* lcpencrypt command line
        """

        print("Let's encrypt {}".format(self.epub_path))

        # Generate a random content id
        content_id = str(uuid.uuid4())
        # Generate a target file path 
        output_filename = "{}-{}.crypt.epub".format(self.epub_filename, content_id)
        output_file_path = os.path.join(
            self.config.encrypted_file_path, output_filename
        )

        # Execute the encryption using the lcpencrypt utility
        return_code, stdout, stderr = util.execute_command([
            self.config.encrypt_cmd_path,
            '-input', self.epub_path,
            '-contentid', content_id,
            '-output', output_file_path])

        if return_code != 0:
            print("Encryption failed, err {}".format(return_code))
            print (stderr)
            return

        # Parse the resulting json message
        result = json.loads(stdout.decode("utf-8"))

        self.encrypted_content_id = result["content-id"]
        self.encrypted_content_encryption_key = result["content-encryption-key"]
        self.encrypted_content_filename = result["protected-content-disposition"]
        self.encrypted_content_location = result["protected-content-location"]
        self.encrypted_content_length= result["protected-content-length"]
        self.encrypted_content_sha256 = result["protected-content-sha256"]

        print("Content id {}".format(self.encrypted_content_id))
        print("Encrypted Content filename {}".format(self.encrypted_content_filename))
        print("Encrypted Content location {}".format(self.encrypted_content_location))
        print("Encrypted Content length {}".format(self.encrypted_content_length))


    def do_store(self, args):
        """
        Store the encrypted epub into the License Server
        """

        if self.encrypted_content_id == None:
            print("encrypt an EPUB file before calling store")
            return

        print("Let's store the encrypted epub {} into the License Server".format(self.encrypted_content_filename))

        encrypted_epub_path = os.path.join(
            self.config.lcp_server_repository_path,
            self.encrypted_content_filename)

        # Prepare request
        path = "/contents/{0}".format(self.encrypted_content_id)
        url = urljoin(self.config.lcp_server_base_uri, path)

        body = json.dumps({
            "content-id": self.encrypted_content_id,
            "content-encryption-key": self.encrypted_content_encryption_key,
            "protected-content-location": encrypted_epub_path,
            "protected-content-length": self.encrypted_content_length,
            "protected-content-sha256": self.encrypted_content_sha256,
            "protected-content-disposition": self.encrypted_content_filename
        })

        # Send request
        try:
            h =  {"Content-Type": "application/json"}
            user = self.config.lcp_server_auth_user
            passwd = self.config.lcp_server_auth_passwd

            r = requests.put(url, headers=h, data=body, auth=(user, passwd))
            if r.status_code not in (requests.codes.ok, requests.codes.created):
                print("Unable to store encrypted epub")
                self.__printLCPServerErrorMsg(r)
                return
        except requests.exceptions.ConnectionError as err:
            print("Connection to server {} failed".format(self.config.lcp_server_base_uri))
            

    def do_license(self, args):
        """
        Generate and fetch a license for the current encrypted epub
        """

        if self.encrypted_content_id == None:
            print("encrypt and store an EPUB file before calling license")
            return

        print("Let's generate a license for {}".format(self.encrypted_content_id))

        # Prepare the request
        path = "/contents/{}/license".format(self.encrypted_content_id)
        url = urljoin(self.config.lcp_server_base_uri, path)
        
        body = json.dumps(self.__build_partial_license())

        # Send the request
        try:
            h =  {"Content-Type": "application/json"}
            user = self.config.lcp_server_auth_user
            passwd = self.config.lcp_server_auth_passwd

            r = requests.post(url, headers=h, data=body, auth=(user, passwd))
            if r.status_code != requests.codes.created:
                print("Unable to create the license.")
                self.__printLCPServerErrorMsg(r)
                return
        except requests.exceptions.ConnectionError as err:
            print("Connection to server failed {}".format(self.config.lcp_server_base_uri))
            return

        # Store the license in the working path
        filename = "{0}-{1}.lcpl".format(self.epub_filename, self.encrypted_content_id)
        file_path = os.path.join(self.config.working_path, filename)        
        # note: a license is short, we can read it in one lump
        with open(file_path, 'w') as file:
            file.write(r.text)

        print("License stored in {}".format(file_path))
        # for later use?
        self.license_path = file_path


    def do_publication(self, args):
        """
        Generate a license and fetch a protected publication for the current encrypted epub
        """
        
        if self.encrypted_content_id == None:
            print("encrypt and store an EPUB file before calling publication")
            return

        print("Let's fetch a protected publication for {}".format(self.encrypted_content_id))

        # Prepare request
        path = "/contents/{0}/publication".format(self.encrypted_content_id)
        url = urljoin(self.config.lcp_server_base_uri, path)

        body = json.dumps(self.__build_partial_license())
          
        # Send the request
        try:
            h =  {"Content-Type": "application/json"}
            user = self.config.lcp_server_auth_user
            passwd = self.config.lcp_server_auth_passwd
           
            # Using the stream param avoid reading the hole file in memory 
            r = requests.post(url, headers=h, data=body, auth=(user, passwd), stream=True)

            if r.status_code != requests.codes.created:
                print("Unable to create the publication.")
                self.__printLCPServerErrorMsg(r)
                return
        except requests.exceptions.ConnectionError as err:
            print("Connection to server failed {}".format(self.config.lcp_server_base_uri))
            return

        # Store the protected publication in the working path
        filename = "{0}-{1}.lcp.epub".format(self.epub_filename, self.encrypted_content_id)
        file_path = os.path.join(self.config.working_path, filename)

        with open(file_path, 'wb') as file:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, file) 

        print("Publication stored in %s", file_path)
        # for later use?
        self.protected_file_path = file_path

            
    def do_EOF(self, line):
        return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="path to the yaml configuration file")
    parser.add_argument("-f", "--file", help="path of a (not protected) EPUB file.")
    args = parser.parse_args()

    # Load the configuration file
    try:
        config = CmdConfig(args.config)
    except FileNotFoundError as err:
        print("Config file not defined or not found")
        return 1

    epub_path = args.file 
    if not os.path.exists(epub_path):
        print("{} not found".format(epub_path))
        return 2

    LCPCmdShell(config, epub_path).cmdloop()

if __name__ == '__main__':
    sys.exit(main())
