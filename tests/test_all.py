import unittest
import test_response, test_request, test_header

if __name__ == '__main__':
    for module in (test_response, test_request, test_header):
        test_suite = unittest.TestLoader().loadTestsFromModule(module)
        unittest.TextTestRunner(verbosity=2).run(test_suite)
