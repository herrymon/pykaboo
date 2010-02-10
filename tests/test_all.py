import unittest
import sys

import os, sys
sys.path.append(os.path.dirname('/home/erick/labs/py/pykaboo'))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango

if __name__ == '__main__':
    test_modules = (
                    'test_response', 
                    'test_request', 
                    'test_header',
                    'test_utils',
                    'test_wsgi',
                    'test_error_middleware'
                   )
    for module in test_modules:
        __import__(module)
        test_module = sys.modules[module]
        test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
        unittest.TextTestRunner(verbosity=2).run(test_suite)
