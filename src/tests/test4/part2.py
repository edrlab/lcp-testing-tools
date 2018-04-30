from  unittest import TestCase
from config.config import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.config = TestConfig('b1')
    license = License(cls.config.license())
    cls.status = Status(license)
    cls.status.update_status()
    cls.original_time = cls.status.get_updated_status()
    cls.original_events = cls.status.get_events()

  def test_a_check_status_active(self):
    """- Check the current status is 'active'"""
    self.assertTrue(self.status.is_active(), "The status is not 'active'")

  def test_b_register_again(self):
    """- Register b1 again with the same id and name string parameters"""
    self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)

  def test_c_check_status_schema(self):
    """- Check that the status document which was returned is valid, using the corresponding JSON schema"""
    try:
      self.status.check_schema()
    except:
      self.fail("Status schema validation failure")

  def test_d_updated_time(self):
    """- Check the the 'updated.status' timestamp has NOT been updated"""
    updated = self.status.get_updated_status()
    self.assertEquals(self.original_time, updated)
    
  def test_f_register_event(self):
    """- Test that NO new register event appears in the status document"""
    self.assertEquals(len(self.original_events), len(self.status.get_events()))
