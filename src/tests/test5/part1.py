from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.config = TestConfig('b2')
    cls.license = License(cls.config.license())
    cls.status = Status(cls.license)
    cls.status.update_status()

  def test_a_check_status_cancelled(self):  
    """- Fetch the status document from this url and Check that the status is 'cancelled' """
    self.assertTrue(self.status.is_cancelled(), "Awaited status is cancel, the returned status is {}".format(self.status.get_status()))
 
  def test_b_check_cancel_event(self):
    """- Test if a new 'cancel' event appears in the status document, display the message """
    events = self.status.get_events()
    if not events is None:
      found = False
      for event in self.status.get_events():
        if event['type'] == 'cancel': 
          found = True

      self.assertTrue(found, "The cancel event is not available in the event list")


  def test_c_check_register_error(self):
    """- Check that a 'register' request returns an error """
    self.status.update_status()
    with self.assertRaisesRegexp(IOError, 'POST .* HTTP error 400$'):
      self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)
