from config.testconfig import TestConfig 
from lcp.license import License
from .base import Test1

class LCPTests(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test1.2')
    self.license = License(self.config.license())

  # test from a -> g are in test1

  def test_h_check_start(self):
    """- Check that right.start parameter is available in the license"""
    self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    """- Check that right.end parameter is available in the license"""
    self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    """- Check the rights expressed in the license; the start date must be before the end date."""
    self.assertTrue(self.license.get_start() < self.license.get_end())

