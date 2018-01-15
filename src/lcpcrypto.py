# -*- coding: utf-8 -*-

"""
License Test suite
LCP crypto utilities

Copyright 2017 European Digital Reading Lab. All rights reserved.
Licensed to the Readium Foundation under one or more contributor license agreements.
Use of this source code is governed by a BSD-style license
that can be found in the LICENSE file exposed on Github (readium) in the project repository.
"""

import logging
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random

LOGGER = logging.getLogger(__name__)


def hash(message, hash_algorithm):
  """
  hash a string value
  params: message - (unicode) string
          hash_algorithm: http://www.w3.org/2001/04/xmlenc#sha256 
  returns: the 32 bytes digest as bytes, or None in case of error
  """
  
  LOGGER.info("lcpcrypto hash")

  # only algo supported: SHA256
  hash = SHA256.new()
  hash.update(message.encode('utf-8'))

  LOGGER.debug("digest (hex) {}".format(hash.hexdigest()))
  LOGGER.debug("digest size {}".format(len(hash.digest())))
  return hash.digest()

def decrypt(data, passphrase_hash, decrypt_algorithm):
  """
  decrypt a bytes value
  params: data - bytes
          passphrase_hash - bytes
          decrypt_algorithm: http://www.w3.org/2001/04/xmlenc#aes256-cbc 
  returns: the decrypted bytes, or None in case of error
  """
  LOGGER.info("lcpcrypto decrypt")
  LOGGER.debug("data {}".format(data))
  LOGGER.debug("hash {}".format(passphrase_hash))
  LOGGER.debug("algo {}".format(decrypt_algorithm))

  # must be 16, 24 or 32 bytes long
  key = passphrase_hash

  iv = data[:AES.block_size]
  # only algo supported: AES256-CBC
  cipher = AES.new(key, AES.MODE_CBC, iv)

  clear_data = unpad(cipher.decrypt( data[AES.block_size:] ))
  LOGGER.debug("clear data {}".format(clear_data))
  return clear_data

def unpad(s):
  LOGGER.debug("c1 {} size {}".format(s, len(s)))
  LOGGER.debug("ord {}".format(ord(s[len(s)-1:])))
  
  
  return s[:-ord(s[len(s)-1:])]