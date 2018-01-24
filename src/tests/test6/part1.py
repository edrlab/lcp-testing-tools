from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  ADAY = 86400 

  def setUp(self):
    # get config
    self.config = TestConfig('test6.1')
    license = License(self.config.license())
    # Get status from config license
    self.status = Status(license)
    self.status.update_status()
    self.end = license.get_end()

  def test_a_renew_non_active_license(self):
    """- Request a loan extension for 2 days only and check that the server responds an error (403 / Forbidden)"""
    self.assertFalse(self.status.is_active(), "The license is active, non active state awaited")
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 403$'):
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, self.end+2*self.ADAY)
 
