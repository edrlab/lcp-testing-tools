from config.config import TestConfig 
from lcp.license import License
from .base import Test1

class LCPTests(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('b1')
    self.license = License(self.config.license())
    
  # All tests are defined in test1

