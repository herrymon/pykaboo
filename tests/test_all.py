import unittest
import sys

import os, sys
# assumes that pykaboo resides in a dir on top of this file
pykaboo_path = os.path.split(os.path.realpath(os.path.dirname(__file__)))[0]
sys.path.append(os.path.dirname(pykaboo_path))

if __name__ == '__main__':
    # assumes that all testcase modules are in the same directory as this file
    test_modules = (
                    'test_response', 
                    'test_request', 
                    'test_utils',
                    'test_wsgi',
                    'test_error_middleware'
                   )
    for module in test_modules:
        __import__(module)
        test_module = sys.modules[module]
        test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
        unittest.TextTestRunner(verbosity=2).run(test_suite)
