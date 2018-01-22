from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test4.1')
    license = License(self.config.license())
    # Get status from config license
    self.status = Status(license)
    self.status.update_status()

  def test_a_check_status_ready(self):
    """- Check the current status is 'ready'"""
    self.assertTrue(self.status.is_ready(), "The status is not 'ready'")

  def test_b_register_and_check_status(self):
    """- Register with non empty id and name string parameters and check the returned status document regarding to status JSON schema"""
    link = self.status.get_link(self.status.REGISTER) 
    self.assertTrue(link['templated'])
    self.status.register(self.status.DEVICEID1, self.status.DEVICENAME1)
    self.assertIsNotNone(status)
    try:
      status.check_schema()
    except:
      self.fail("Status schema validation failure")


