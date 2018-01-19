from config.testconfig import TestConfig 
from lcp.license import License
from .test3 import Test3

class Test32(Test3):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.2')
    self.license = License(self.config.license())
