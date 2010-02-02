import unittest
import sys

if __name__ == '__main__':
    test_modules = (
                    'test_response', 
                    'test_request', 
                    'test_header'
                   )
    for module in test_modules:
        __import__(module)
        test_module = sys.modules[module]
        test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
        unittest.TextTestRunner(verbosity=2).run(test_suite)
