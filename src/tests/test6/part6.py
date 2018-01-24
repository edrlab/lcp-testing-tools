from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  ADAY = 86400 

  def setUp(self):
    # get config
    self.config = TestConfig('l1')
    license = License(self.config.license())
    # Get status from config license
    self.status = Status(license)
    self.status.update_status()
    self.end = license.get_end()

  def test_a_renew_license_before_end_date(self):
    """- Request a loan extension with an erroneous timestamp"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 400$'):
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, 'testrenew')
