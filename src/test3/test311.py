import urllib
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status
from test1.test1 import Test1


class Test311(Test1):

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
    

  # All tests are defined in test1

