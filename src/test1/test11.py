from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.lcp import License

class Test11(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test1.1')
    self.license = License(self.config.license(), self.config.schema())
     
  def test_a_check_license_schema(self):
      self.assertTrue(self.license.check_schema())

  def test_b_check_certificate_validity(self):
    cacert = self.config.cacert()
    self.assertTrue(self.license.check_certificate(self.config.cacert()))

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

