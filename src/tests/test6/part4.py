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
    """- Request a loan extension for 2 days after the current end date, with a proper id and name"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    self.status.renewnodevice(self.end+2*self.ADAY)

  def test_b_check_status_document(self):
    """- Check status is always active and check that the updated status document is valid"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    try:
      self.status.check_schema()
    except:
      self.fail("Status schema validation failure")

  def test_c_check_renew_event(self):
    """- If events are present, check if the status document contains a new 'renewed' event"""
    pass

  def test_d_fetch_license_and_check_end_date(self):
    """- Fetch the license and check that the new end date is still the previous expiration date"""
    license = self.status.update_license()
    self.assertEquals(license.get_end(), self.end+2*self.ADAY)
