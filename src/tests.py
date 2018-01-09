import unittest
from test1.test11 import Test11


if __name__ == '__main__':
  test11 = unittest.TestLoader().loadTestsFromTestCase(Test11)
  alltests = unittest.TestSuite([test11])
  unittest.TextTestRunner(verbosity=2).run(alltests)
