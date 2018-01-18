from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.epub import ePub
from test1.test1 import Test1


class Test22(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test2')
    epub = ePub(self.config.epub())
    self.license = License(epub.read(epub.LCP_LICENSE), raw = True)

  # test a -> g are in test1
  def test_h_check_start(self):
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    if self.license.is_loan():
      self.assertTrue(self.license.get_start() < self.license.get_end())

