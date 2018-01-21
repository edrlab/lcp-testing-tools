import unittest
import sys
import os
import argparse
import inspect
from datetime import datetime

TESTSUITES=[
  {'module': 'tests.test1.part1', 'title': 'Test1.1 LCP buy license basic tests' },
  {'module': 'tests.test1.part2', 'title': 'Test1.2 LCP loan license basic tests' },
  {'module': 'tests.test2.part1', 'title': 'Test2.1 LCP encrypted ePub tests' },
  {'module': 'tests.test2.part2', 'title': 'Test2.1 LCP encrypted ePub license tests' },
  {'module': 'tests.test3.part1', 'title': 'Test3.1 Status document buy license basic tests' },
  {'module': 'tests.test3.part2', 'title': 'Test3.2 Status document loan license basic tests' }
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
    self.log.write('------------------------------------------------------------------\n')
    self.log.write(now+self.title+'\n')
    self.log.write('------------------------------------------------------------------\n')

  def startTest(self, test):
    self.log.write(test.shortDescription()+'... ')
    pass

  def stopTest(self, test):
    self.log.write('\n')
    pass

  def addError(self, test, err):
    self.errors.append((test, err))
    self.log.write('ERROR')

  def addFailure(self, test, err):
    self.failures.append((test, err))
    self.log.write('FAILURE')

  def addSuccess(self, test):
    self.log.write('OK')

  def end(self):
    if len(self.errors) > 0:
      print self.errors
    if len(self.failures) > 0:
      print self.failures
    if len(self.failures) == 0 and len(self.errors) == 0:
      self.log.write('--> All tests are OK\n')



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--config", required=True, help="path to the yaml configuration file", dest='config')
  parser.add_argument("-f", "--file", required=True, help="Tests log file", dest='file')
  args = parser.parse_args()

  os.environ['LCP_TEST_CONFIG'] = args.config

  for testsuite in TESTSUITES:
    with open(args.file, 'aw') as logfile:
      tests = get_tests(testsuite['module'])
      r = LCPTestResult(logfile, testsuite['title'])
      r.start()
      for test in tests:
        test.run(r)
      r.end()
