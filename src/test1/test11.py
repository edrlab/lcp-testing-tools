from  unittest import TestCase
from config.testconfig import TestConfig 
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time

class Test11(TestCase):

  def _getlink(self, license, name):
    for link in license['links']:
      if link['rel'] == name:
        return link
    return None

  def setUp(self):
    # get config
    self.config = TestConfig(self)
    # get crypto from external crypto tool
    self.crypto = self.config.crypto_package()

     
  def test_a_check_license_schema(self):
    schema = self.config.json_license_schema()
    license = self.config.json_license()
    jsonvalidate(license, schema)

  def test_b_check_certificate_validity(self):
    cacert = self.config.cacert()
    license = self.config.json_license()
    certificate = license['signature']['certificate']
    issued = license['issued']
    unix_time = time.mktime(dateparse(issued).timetuple())  
    self.assertTrue(self.crypto.verify_certificate(str(certificate), str(cacert), int(unix_time)))

  def test_c_check_license_signature(self):
    license = self.config.json_license()
    certificate = str(license['signature']['certificate'])
    # signature algorithm is checked by schema (test_a_check_license_schema)  
    signature = str(license['signature']['value'])
    canonical = self.crypto.canonical(self.config.raw_license())
    self.assertTrue(self.crypto.verify_sign_sha256(signature, certificate, canonical))

  def test_d_check_publication_mimetype(self):
    license = self.config.json_license()
    link = self._getlink(license, 'publication')
    self.assertIsNotNone(link)
    self.assertEquals(self.config.publication_mimetype(), link['type'])
  
  def test_e_check_status_mimetype(self):
    license = self.config.json_license()
    link = self._getlink(license, 'status')
    self.assertIsNotNone(link)
    self.assertEquals(self.config.status_mimetype(), link['type'])
   
  def test_f_check_content_key_format(self):
    license = self.config.json_license()
    # content_key value and content_key algorithm are checked by schema (test_a_check_license_schema)
    content_key = self.crypto.base64_decode(str(license['encryption']['content_key']['encrypted_value']))
    self.assertEquals(len(content_key), 64)

  def test_g_check_key_check(self):
    license = self.config.json_license()
    # user_key algorithm is checked by schema (test_a_check_license_schema)
    user_key_hash_algo = str(license['encryption']['user_key']['algorithm'])
    content_key_encryption_algo = str(license['encryption']['content_key']['algorithm'])
    user_key = self.crypto.userkey(self.config.passphrase(), user_key_hash_algo)
    key_check = str(license['encryption']['user_key']['key_check'])
    license_id = str(license['id'])
    self.assertTrue(self.crypto.check_userkey(self.config.passphrase(), user_key_hash_algo,
                key_check, license_id, content_key_encryption_algo))

