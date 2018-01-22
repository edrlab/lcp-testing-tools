from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status

class LCPTests(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test4')
    license = License(self.config.license())
    # Get status from config license
    self.status = Status(license)
    self.status.update_status()

  def test_a_register_without_id_and_name(self):
    """- Register b1 without id and name string parameters and check that the server returns an error"""
    # Save updated.status to compare on test_e...
    with self.assertRaises(IOError):
      self.status.register('', '')
