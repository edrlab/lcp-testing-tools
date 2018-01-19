import unittest
import sys
import os
import argparse
from datetime import datetime

from test1.test11 import Test11
from test1.test12 import Test12
from test2.test21 import Test21
from test2.test22 import Test22
from test3.test31 import Test31
from test3.test32 import Test32
from test3.test311 import Test311
from test3.test321 import Test321

def log(logfile, msg):
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S - ')
  sys.stdout.write(now+msg+'\n')
  logfile.write('\n'+now+msg+'\n')


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--config", required=True, help="path to the yaml configuration file", dest='config')
  parser.add_argument("-f", "--file", required=True, help="Tests log file", dest='file')
  args = parser.parse_args()

  os.environ['LCP_TEST_CONFIG'] = args.config
  test11 = unittest.TestLoader().loadTestsFromTestCase(Test11)
  test12 = unittest.TestLoader().loadTestsFromTestCase(Test12)
  test21 = unittest.TestLoader().loadTestsFromTestCase(Test21)
  test22 = unittest.TestLoader().loadTestsFromTestCase(Test22)
  test31 = unittest.TestLoader().loadTestsFromTestCase(Test31)
  test32 = unittest.TestLoader().loadTestsFromTestCase(Test32)
  test311 = unittest.TestLoader().loadTestsFromTestCase(Test311)
  test321 = unittest.TestLoader().loadTestsFromTestCase(Test321)

  with open(args.file, 'w') as logfile:
    log(logfile, "Executing Test1.1 fron config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, descriptions=True, verbosity=2).run(test11)
    log(logfile, "Executing Test1.2 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test12)
    log(logfile, "Executing Test2.1 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test21)
    log(logfile, "Executing Test2.2 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test22)
    log(logfile, "Executing Test3.1 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test31)
    unittest.TextTestRunner(logfile, verbosity=2).run(test311)
    log(logfile, "Executing Test3.2 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test32)
    unittest.TextTestRunner(logfile, verbosity=2).run(test321)
