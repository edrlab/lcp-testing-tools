import unittest
from test1.test11 import Test11
from test1.test12 import Test12


if __name__ == '__main__':
  test11 = unittest.TestLoader().loadTestsFromTestCase(Test11)
  test12 = unittest.TestLoader().loadTestsFromTestCase(Test12)
  alltests = unittest.TestSuite([test11, test12])
  unittest.TextTestRunner(verbosity=2).run(alltests)
