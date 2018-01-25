from config.config import TestConfig 
from lcp.license import License
from .base import Test1

class LCPTests(Test1):

  @classmethod
  def setUpClass(cls):
    cls.config = TestConfig('b1')
    cls.license = License(cls.config.license())

  # All tests are defined in test1

