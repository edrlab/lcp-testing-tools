from config.testconfig import TestConfig 
from lcp.license import License
from test1 import Test1

class Test12(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test1.2')
    self.license = License(self.config.license())

  # test from a -> g are in test1

  def test_h_check_start(self):
    self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    self.assertTrue(self.license.get_start() < self.license.get_end())

