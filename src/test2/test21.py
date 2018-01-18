from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.epub import ePub
from os.path import splitext

class Test21(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test2')
    self.epub = ePub(self.config.epub())
    self.encxml = self.epub.get_encryption_xml()

  def test_a_check_encryptionxml(self):
    self.assertTrue(self.epub.contains(self.epub.ENCRYPTION_XML))

  def test_b_check_encryptionxml_format(self):
    self.assertTrue(self.encxml.check_schema())

  def test_c_check_encryptionxml_items(self):
    for uri in self.encxml.get_all_uri():
      self.assertTrue(self.epub.contains(uri))

  def test_d_check_unencrypted_resources(self): 
    encrypted = self.encxml.get_all_uri()
    for unencrypted in self.epub.UNENCRYPTED_FILES:
      self.assertFalse(unencrypted in encrypted)

  def test_e_check_media_uncompressed(self): 
    for comp in self.encxml.get_compressed_uri():
      name, ext = splitext(comp)
      self.assertFalse(ext in self.epub.MEDIA_EXTENSIONS)

  def test_f_check_license_is_available(self):
    self.assertTrue(self.epub.contains(self.epub.LCP_LICENSE))
