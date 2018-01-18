from  unittest import TestCase
from config.testconfig import TestConfig 
from lcp.license import License
from lcp.status import Status
import urllib

class Test31(TestCase):

  def setUp(self):
    # get config
    self.config = TestConfig('test3.1')
    self.license = License(self.config.license())

     
  def test_a_check_status_link_https(self):
    link = self.license.get_link('status', 'href')
    self.assertTrue(link.startswith('https://'))

  def test_b_check_status_document(self):
    link = self.license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    self.assertIsNotNone(status)
    try:
      status.check_schema()
    except:
      self.fail("Status schema validation failure")

  def test_c_status_events(self):
    link = self.license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    events = status.get_events()
    # TODO: warning message if there is no events

  def test_d_check_status_license_link(self):
    link = self.license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    link = status.get_link('license', 'href')
    self.assertIsNotNone(link)
    self.assertTrue(link.startswith('https://'))

  def test_e_check_license_mimetype(self):
    link = self.license.get_link('status', 'href')
    response = urllib.urlopen(link)
    status = Status(response.read())
    mimetype = status.get_link('license', 'type')
    self.assertEquals(mimetype, License.MIMETYPE)
