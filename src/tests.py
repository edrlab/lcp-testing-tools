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
from test4.test41 import Test41


def log(logfile, msg):
  now = datetime.now().strftime('%Y-%m-%d %H:%M:%S - ')
  sys.stdout.write(now+msg+'\n')
  logfile.write('\n'+now+msg+'\n')


class LCPTestResult(unittest.TestResult):
  def __init__(self, log):
    try: # Python 3
      super().__init__()
    except:
      super(LCPTestResult, self).__init__()
    self.log = log

  def startTestRun(self):
    # before all tests
    pass

  def stopTestRun(self):
    # After all tests
    pass

  def startTest(self, test):
    # Before each test
    pass

  def stopTest(self, test):
    # After each test
    pass

  def addError(self, test, err):
    pass

  def addFailure(test, err):
    pass

  def addSuccess(self, test):
    pass



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
  test41 = unittest.TestLoader().loadTestsFromTestCase(Test41)

  r = LCPTestResult()
  for t in test11:
    t.run(result = r)



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
    log(logfile, "Executing Test4.1 from config {} and log activity to {}".format(args.config, args.file))
    unittest.TextTestRunner(logfile, verbosity=2).run(test41)
