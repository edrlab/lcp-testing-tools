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

  def test_a_renew_license_before_end_date(self):
    """- Request a loan extension with an erroneous timestamp"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 400$'):
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, 'testrenew')
