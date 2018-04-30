from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    # get config
    cls.config = TestConfig('b1')
    license = License(cls.config.license())
    # Get status from config license
    cls.status = Status(license)
    cls.status.update_status()
    cls.original_time = cls.status.get_updated_status()

  def test_a_check_status_ready(self):
    """- Check the current status is 'ready'"""
    self.assertTrue(self.status.is_ready(), "The status is not 'ready'")

  def test_b_register_and_check_status(self):
    """- Register with non empty id and name string parameters"""
    link = self.status.get_link(self.status.REGISTER) 
    self.assertTrue(link['templated'], "The register link is not templated")
    # Save updated.status to compare on test_e...
    self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_c_check_status_schema(self):
    """- Check that the status document which was returned is valid, using the corresponding JSON schema"""
    try:
      self.status.check_schema()
    except:
      self.fail("Status schema validation failure")

  def test_d_check_status_active(self):
    """- Check that a new status is 'active'"""
    self.assertTrue(self.status.is_active(), "After a register, the license has to be active")

  def test_e_updated_time(self):
    """- Check the the 'updated.status' timestamp has been updated"""
    self.assertLess(self.original_time, self.status.get_updated_status(), "The status update time need to be updated after a register action")
    
  def test_f_register_event(self):
    """- Test if a new register event appears in the status document"""
    events = self.status.get_events()
    if not events is None:
      found = False
      for event in self.status.get_events():
        if event['type'] == 'register' and event['id'] == self.status.DEVICEID1 and event['name'] == self.status.DEVICENAME1: 
          found = True

      self.assertTrue(found, "The register event is not available in the event list")

