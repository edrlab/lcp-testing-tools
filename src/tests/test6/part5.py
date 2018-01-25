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
    """- Request a loan extension for 2 days after the current end date, with a proper id and name"""
    self.assertTrue(self.status.is_active(), "The license is not active, active state awaited")
    self.status.renewnoend(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_b_check_status_document(self):
    """- Check status is always active and check that the updated status document is valid"""
    try:
      self.status.check_schema()
    except:
      self.fail("Status schema validation failure")

  def test_c_fetch_license_and_check_end_date(self):
    """- Fetch the license and check that the new end date is still the previous expiration date"""
    license = self.status.update_license()
    end = license.get_end()
    # TODO: check end with awaited renew period
