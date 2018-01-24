from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  def setUp(self):
    self.config = TestConfig('b2')
    self.license = License(self.config.license())

  def test_a_check_status_cancelled(self):  
    """- Fetch the status document from this url and Check that the status is 'cancelled' """
    status = Status(self.license)
    status.update_status()
    self.assertTrue(status.is_cancelled())
 
  def test_b_check_cancel_event(self):
    """- Test if a new 'cancelled' event appears in the status document, display the message """
    pass

  def test_c_check_register_error(self):
    """- Check that a 'register' request returns an error """
    status = Status(self.license)
    status.update_status()
    with self.assertRaisesRegexp(IOError, 'POST .* HTTP error 400$'):
      status.register(status.DEVICEID1, status.DEVICENAME1)
