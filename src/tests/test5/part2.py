from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.config = TestConfig('b3')
    cls.license = License(cls.config.license())
    cls.status = Status(cls.license)
    cls.status.update_status()

  def test_a_check_status_cancelled(self):  
    """- Fetch the status document from this url and Check that the status is 'revoked' """
    self.assertTrue(self.status.is_revoked())
 
  def test_b_check_revoked_event(self):
    """- Test if a new 'revoke' event appears in the status document, display the message """
    events = self.status.get_events()
    if not events is None:
      found = False
      for event in self.status.get_events():
        if event['type'] == self.status.REVOKE:
          found = True

      self.assertTrue(found, "The cancel event is not available in the event list")



  def test_c_check_register_error(self):
    """- Check that a 'register' request returns an error """
    with self.assertRaisesRegexp(IOError, 'POST .* HTTP error 400$'):
      self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)
