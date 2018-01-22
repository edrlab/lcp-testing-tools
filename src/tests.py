import unittest
import sys
import os
import argparse
import inspect
import traceback
from datetime import datetime
from config.testconfig import TestConfig

TESTSUITES=[
  {'module': 'tests.test1.part1', 'title': 'Test1.1 LCP buy license basic tests' },
  {'module': 'tests.test1.part2', 'title': 'Test1.2 LCP loan license basic tests' },
  {'module': 'tests.test2.part1', 'title': 'Test2.1 LCP encrypted ePub tests' },
  {'module': 'tests.test2.part2', 'title': 'Test2.1 LCP encrypted ePub license tests' },
  {'module': 'tests.test3.part1', 'title': 'Test3.1 Status document buy license basic tests' },
  {'module': 'tests.test3.part2', 'title': 'Test3.2 Status document loan license basic tests' },
  {'module': 'tests.test4.part1', 'title': 'Test4.1 Check first register' },
  {'module': 'tests.test4.part2', 'title': 'Test4.2 Check several registers' },
  {'module': 'tests.test4.part3', 'title': 'Test4.3 Check register error' }
]

def get_tests(module):
  tests = []
  t = __import__(module, fromlist=['Tests'])
  for name, obj in inspect.getmembers(t):
    if inspect.isclass(obj) and name.startswith('LCPTests'):
      tests.append(unittest.TestLoader().loadTestsFromTestCase(obj))
  return tests 

# Test result class to format test results
class LCPTestResult(unittest.TestResult):
  def __init__(self, log, title):
    try: # Python 3
      super().__init__()
    except:
      super(LCPTestResult, self).__init__()
    self.log = log
    self.title = title

  def start(self):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S - ')
    msg = now+self.title+'\n'
    self.log.write('\n------------------------------------------------------------------\n')
    self.log.write(msg)
    self.log.write('------------------------------------------------------------------\n')
    sys.stdout.write(msg)

  def startTest(self, test):
    self.log.write(test.shortDescription()+'... ')
    sys.stdout.write(test.shortDescription()+'... ')
    pass

  def stopTest(self, test):
    self.log.write('\n')
    sys.stdout.write('\n')
    pass

  def addError(self, test, err):
    self.errors.append((test, err))
    self.log.write('ERROR')
    sys.stdout.write('ERROR')

  def addFailure(self, test, err):
    self.failures.append((test, err))
    self.log.write('FAILURE')
    sys.stdout.write('FAILURE')

  def addSuccess(self, test):
    self.log.write('OK')
    sys.stdout.write('OK')

  def end(self):
    self.log.write('======= Error summary =======\n')
    for err in self.errors:
      testname = err[0].shortDescription()
      errmsg = err[1][1]
      self.log.write('{}: {}\n'.format(testname, errmsg))
      traceback.print_tb(err[1][2], file=self.log)
    for err in self.failures:
      testname = err[0].shortDescription()
      errmsg = err[1][1]
      self.log.write('{}: {}\n'.format(testname, errmsg))
      traceback.print_tb(err[1][2], file=self.log)
    if len(self.failures) == 0 and len(self.errors) == 0:
      self.log.write('--> All tests are OK\n')
    self.log.write('=============================\n')



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--config", required=True, help="path to the yaml configuration file", dest='config')
  args = parser.parse_args()

  # Set configuration file
  os.environ['LCP_TEST_CONFIG'] = args.config
  # Get config from config file 
  config = TestConfig()
  now = datetime.now().strftime('%Y%m%d_%H%M%S')
  filename = '{}-{}.log'.format(config.provider(), now)

  for testsuite in TESTSUITES:
    with open(filename, 'aw') as logfile:
      tests = get_tests(testsuite['module'])
      r = LCPTestResult(logfile, testsuite['title'])
      r.start()
      for test in tests:
        test.run(r)
      r.end()
