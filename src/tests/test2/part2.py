from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.epub import ePub
from tests.test1.base import Test1


class LCPTests(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test2')
    epub = ePub(self.config.epub())
    self.license = License(epub.read(epub.LCP_LICENSE), raw = True)

  # test a -> g are in test1
  def test_h_check_start(self):
    """- Check that right.start parameter is available in the license"""
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    """- Check that right.end parameter is available in the license"""
    if self.license.is_loan():
      self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    """- Check the rights expressed in the license; the start date must be before the end date."""
    if self.license.is_loan():
      self.assertTrue(self.license.get_start() < self.license.get_end())

