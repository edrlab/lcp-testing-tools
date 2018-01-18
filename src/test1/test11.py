from config.testconfig import TestConfig 
from lcp.license import License
from test1 import Test1

class Test11(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test1.1')
    self.license = License(self.config.license())
    
  # All tests are defined in test1

