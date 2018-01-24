from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status
from .base import Test3
from tests.test1.base import Test1

class LCPTests1(Test3):

  def setUp(self):
    # get config
    self.config = TestConfig('b1')
    self.license = License(self.config.license())


class LCPTests2(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('b1')
    license = License(self.config.license())
    status = Status(license)
    status.update_status()

    # Get license from status
    self.license = status.update_license()
 
