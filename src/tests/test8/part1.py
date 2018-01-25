from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status
import time

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('l2')
    license = License(cls.config.license())
    # Get status from config license
    cls.status = Status(license)
    cls.status.update_status()

  def test_a_return_license(self):
    """- Check that the status is 'expired'"""
    self.assertTrue(self.status.is_expired(), "The awaited status is expired, the current status is {}".format(self.status.get_status()))

  def test_b_check_return_again(self):
    """- Check that a 'register' request returns an error."""
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 4[0-9][0-9]$'):
      self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_c_check_license_end(self):
    """- Check that the 'end' datetime is before now"""
    license = self.status.update_license()
    end = license.get_end()
    now = int(time.time())
    self.assertLess(end, now)
