from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('l1')
    license = License(cls.config.license())
    # Get status from config license
    cls.status = Status(license)
    cls.status.update_status()
    cls.end = license.get_end()

  def test_a_return_license(self):
    """- Request a return, with a proper id and name"""
    self.status.licensereturn(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_b_check_status_is_returned(self):
    """- Check that new status is 'returned'"""
    self.assertTrue(self.status.is_returned(), "The awaited status is returned, the current status is {}".format(self.status.get_status()))

  def test_c_check_return_event(self):
    """- Test if the status document contains a new 'return' event"""
    events = self.status.get_events()
    if not events is None:
      found = False
      for event in self.status.get_events():
        if event['type'] == self.status.RETURN:
          found = True

      self.assertTrue(found, "The return event is not available in the event list")

  def test_d_check_return_again(self):
    """- Check that a 'register' request returns an error."""
    with self.assertRaisesRegexp(IOError, 'PUT .* HTTP error 400$'):
      self.status.licensereturn(self.status.DEVICEID1, self.status.DEVICENAME1)
