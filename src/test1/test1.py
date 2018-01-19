from  unittest import TestCase

class Test1(TestCase):
  longMessage = True
  """Basic LCP license testing"""
  def test_a_check_license_schema(self):
    """- Check b1 using the JSON schema provided by EDRLab"""
    try:
      self.license.check_schema()
    except:
      self.fail("License schema validation failure")

  def test_b_check_certificate_validity(self):
    """- Check certificate validity, relative to the CA and license issued date/time"""
    self.assertTrue(self.license.check_certificate(), "The certificate is not valid regarding to CA certificate, license issued time and CRL")

  def test_c_check_license_signature(self):
    """- Check the signature value"""
    self.assertTrue(self.license.check_signature())

  def test_d_check_publication_mimetype(self):
    """- Check that the mime-type of a publication link is 'application/epub+zip' """
    self.assertEquals(self.config.publication_mimetype(), self.license.get_link('publication', 'type'))
  
  def test_e_check_status_mimetype(self):
    """- Check that the mime-type of a status link is 'application/vnd.readium.license.status.v1.0+json' """
    self.assertEquals(self.config.status_mimetype(), self.license.get_link('status', 'type'))
   
  def test_f_check_content_key_format(self):
    """- Check the content key format (64 bytes after base64 decoding)"""
    self.assertEquals(len(self.license.get_content_key()), 64)

  def test_g_check_key_check(self):
    """Check the key_check value"""
    self.assertTrue(self.license.check_user_key(self.config.passphrase()))

