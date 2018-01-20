from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status
import urllib

class Test41(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test4.1')
    license = License(self.config.license())
    # Get status from config license
    link = license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())


  def test_a_check_status_ready(self):
    """- Check the current status is 'ready'"""
    self.assertTrue(status.is_ready(), "The status is not 'ready'")

