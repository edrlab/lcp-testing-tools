from  unittest import TestCase
from config.testconfig import TestConfig 
from jsonschema import validate as jsonvalidate
from dateutil.parser import parse as dateparse
import time

class Test11(TestCase):
    def setUp(self):
      # get config
      self.config = TestConfig(self)
      # get crypto from external crypto tool
      self.crypto = self.config.crypto_package()

     
    def test_a_check_license_schema(self):
      schema = self.config.json_license_schema()
      license = self.config.json_license()
      jsonvalidate(license, schema)

    def test_b_check_certificate_validity(self):
      cacert = self.config.cacert()
      license = self.config.json_license()
      certificate = license['signature']['certificate']
      issued = license['issued']
      unix_time = time.mktime(dateparse(issued).timetuple())  
      self.assertTrue(self.crypto.verify_certificate(str(certificate), str(cacert), int(unix_time)))


