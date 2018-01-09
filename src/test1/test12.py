from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.lcp import License

from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time

class Test12(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test1.2')
    # get crypto from external crypto tool
    self.crypto = self.config.crypto_package()
    self.license = License(self.config.license(), self.config.schema())

     
  def test_a_check_license_schema(self):
      self.assertTrue(self.license.check_schema())

  def test_b_check_certificate_validity(self):
    cacert = self.config.cacert()
    certificate = self.license.get_certificate()
    issued = self.license.get_issued()
    self.assertTrue(self.crypto.verify_certificate(certificate, cacert, issued))

  def test_c_check_license_signature(self):
    certificate = self.license.get_certificate()
    # signature algorithm is checked by schema (test_a_check_license_schema)  
    signature = self.license.get_signature()
    canonical = self.license.get_canonical()
    self.assertTrue(self.crypto.verify_sign_sha256(signature, certificate, canonical))

  def test_d_check_publication_mimetype(self):
    self.assertEquals(self.config.publication_mimetype(), self.license.get_link('publication', 'type'))
  
  def test_e_check_status_mimetype(self):
    self.assertEquals(self.config.status_mimetype(), self.license.get_link('status', 'type'))
   
  def test_f_check_content_key_format(self):
    self.assertEquals(len(self.license.get_content_key()), 64)

  def test_g_check_key_check(self):
    self.assertTrue(self.license.check_user_key(self.config.passphrase()))

  def test_h_check_start(self):
    self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    self.assertTrue(self.license.get_start() < self.license.get_end())
