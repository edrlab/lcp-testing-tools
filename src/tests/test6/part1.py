from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  ADAY = 86400 

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('l1')
    license = License(cls.config.license())
    # Get status from config license
    cls.status = Status(license)
    cls.status.update_status()
    cls.end = license.get_end()

  def test_a_renew_non_active_license(self):
    """- Request a loan extension for 2 days only and check that the server responds an error (HTTP/4xx)"""
    self.assertTrue(self.status.is_ready(), "The license is active, non active state awaited")
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 4[0-9][0-9]$'):
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, self.end+2*self.ADAY)
 
