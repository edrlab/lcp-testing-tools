import urllib
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status
from test1.test1 import Test1


class Test321(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.2')
    license = License(self.config.license())
    # Get status from config license
    link = license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    # Get license from status
    link = status.get_link('license', 'href')
    response = urllib.urlopen(link)
    self.license = License(response.read(), raw = True)
    
  # test from a -> g are in test1

  def test_h_check_start(self):
    self.assertIsNotNone(self.license.get_start())

  def test_i_check_end(self):
    self.assertIsNotNone(self.license.get_end())

  def test_j_check_start_before_end(self):
    self.assertTrue(self.license.get_start() < self.license.get_end())

