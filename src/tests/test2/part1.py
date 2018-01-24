from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.epub import ePub
from os.path import splitext

class LCPTests(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('e1')
    self.epub = ePub(self.config.epub())
    self.encxml = self.epub.get_encryption_xml()

  def test_a_check_encryptionxml(self):
    """- Check that encryption.xml is present in the protected publication"""
    self.assertTrue(self.epub.contains(self.epub.ENCRYPTION_XML))

  def test_b_check_encryptionxml_format(self):
    """- Check the xml file format regarding schema"""
    self.assertTrue(self.encxml.check_schema())

  def test_c_check_encryptionxml_items(self):
    """- Check that all resources referenced in encryption.xml are found in the EPUB archive."""
    for uri in self.encxml.get_all_uri():
      self.assertTrue(self.epub.contains(uri))

  def test_d_check_unencrypted_resources(self): 
    """- Check unencrypted resources (mainly META-INF ones)"""
    encrypted = self.encxml.get_all_uri()
    for unencrypted in self.epub.UNENCRYPTED_FILES:
      self.assertNotIn(unencrypted, encrypted)

  def test_e_check_media_uncompressed(self): 
    """- Check that media resources are not compressed"""
    for comp in self.encxml.get_compressed_uri():
      name, ext = splitext(comp)
      self.assertNotIn(ext, self.epub.MEDIA_EXTENSIONS)

  def test_f_check_license_is_available(self):
    """- Check that license.lcpl is present in the protected publication"""
    self.assertTrue(self.epub.contains(self.epub.LCP_LICENSE))
