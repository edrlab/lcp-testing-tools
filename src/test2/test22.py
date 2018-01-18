from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.epub import ePub

class Test22(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test2')
    epub = ePub(self.config.epub())
    self.license = License(epub.read(epub.LCP_LICENSE), raw = True)

  # tests from test1
  def test_b_check_certificate_validity(self):
    self.assertTrue(self.license.check_certificate())

  def test_c_check_license_signature(self):
    self.assertTrue(self.license.check_signature())

  def test_d_check_publication_mimetype(self):
    self.assertEquals(self.config.publication_mimetype(), self.license.get_link('publication', 'type'))
  
  def test_e_check_status_mimetype(self):
    self.assertEquals(self.config.status_mimetype(), self.license.get_link('status', 'type'))
   
  def test_f_check_content_key_format(self):
    self.assertEquals(len(self.license.get_content_key()), 64)

  def test_g_check_key_check(self):
    self.assertTrue(self.license.check_user_key(self.config.passphrase()))

  def test_h_check_start(self):
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    if self.license.is_loan():
      self.assertTrue(self.license.get_start() < self.license.get_end())

