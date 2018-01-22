from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status 
from .base import Test3
from tests.test1.base import Test1


class LCPTests1(Test3):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.2')
    self.license = License(self.config.license())


class LCPTests2(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.2')
    license = License(self.config.license())
    # Get status from config license
    status = Status(license)
    status.update_status()
    self.license = status.update_license()
    
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

