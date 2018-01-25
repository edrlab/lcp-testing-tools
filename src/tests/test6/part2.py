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

  def test_a_register_device_for_loan_license(self):
    """- Register the device for l1"""
    self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_b_renew_license_before_end_date(self):
    """- Request a loan extension for an new end date before the current expiration date, with a proper id and name and check that the updated status document is valid or the server responds in error  (403 / Forbidden)"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 403$'):
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, self.end-2*self.ADAY)

  def test_c_fetch_license_and_check_end_date(self):
    """- Fetch the license and check that the new end date is still the previous expiration date"""
    license = self.status.update_license()
    self.assertEquals(license.get_end(), self.end)
