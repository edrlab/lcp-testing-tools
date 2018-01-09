from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.lcp import License
from lcp.epub import ePub

class Test21(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test2.1')
    self.epub = ePub(self.config.epub())

  def test_a_check_encryptionxml(self):
    pass

  def test_b_check_encryptionxml_format(self):
    pass

  def test_c_check_encryptionxml_items(self):
    pass

  def test_d_check_unencrypted_resources(self): 
    pass

  def test_e_check_media_uncompressed(self): 
    pass

  def test_f_check_license(self):
    pass

