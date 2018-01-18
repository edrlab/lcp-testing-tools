from  unittest import TestCase

class Test1(TestCase):

  def test_a_check_license_schema(self):
    try:
      self.license.check_schema()
    except:
      self.fail("License schema validation failure")

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

