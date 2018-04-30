from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status 
from .base import Test3
from tests.test1.base import Test1


class LCPTests1(Test3):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('l1')
    cls.license = License(cls.config.license())


class LCPTests2(Test1):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('l1')
    license = License(cls.config.license())
    # Get status from config license
    status = Status(license)
    status.update_status()
    cls.license = status.update_license()
    
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

