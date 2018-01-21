from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status
import urllib
from .base import Test3
from tests.test1.base import Test1

class LCPTests1(Test3):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.1')
    self.license = License(self.config.license())


class LCPTests2(Test1):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.1')
    license = License(self.config.license())
    # Get status from config license
    link = license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    # Get license from status
    link = status.get_link('license', 'href')
    response = urllib.urlopen(link)
    self.license = License(response.read(), raw = True)
 
