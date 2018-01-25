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

  def test_a_renew_license_at_potential_rights_end_date(self):
    """- If a potential rights end is present, request loan renew until the potential rights end is reached"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    potential_end = self.status.get_potential_end()
    if not potential_end is None:
      self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, potential_end)
      license = self.status.update_license()
      self.assertEquals(potential_end, license.get_end(), "The new end date of the license is not potential_rights.end")
    
  def test_b_renew_license_after_potential_rights_end_date(self):
    """- Request a new loan renew, with a date after potential_right.end and check that the server returns an error"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    potential_end = self.status.get_potential_end()
    if not potential_end is None:
      with self.assertRaisesRegexp(IOError, 'POST .* HTTP error 403$'):
        self.status.renew(self.status.DEVICEID1, self.status.DEVICENAME1, potential_end+self.ADAY)

