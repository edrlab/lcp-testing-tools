from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status
from .base import Test3
from tests.test1.base import Test1

class LCPTests1(Test3):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('b1')
    cls.license = License(cls.config.license())
    print("\nlicence name", cls.config.license())



class LCPTests2(Test1):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('b1')
    license = License(cls.config.license())
    status = Status(license)
    status.update_status()

    # Get license from status
    cls.license = status.update_license()
