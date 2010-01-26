import __init__
import unittest
from pykaboo.pyka import Header

class TestHeaderAttributes(unittest.TestCase):
    """
        test if Header sets default attributes as intended
        test adding of new headers
        test changing state of header
    """
    def setUp(self):
        self.header = Header('200 OK', ('Content-Type', 'text/html'))

    def test_init_state(self):
        # test state
        actual = self.header.pack[0]
        expected = '200 OK'
        self.assertEqual(actual, expected)

    def test_init_headers(self):
        actual = self.header.pack[1]
        expected = [('Content-Type', 'text/html')]
        self.assertEqual(actual, expected)

    def test_change_state(self):
        expected = '404 NOT FOUND'
        self.header.state(expected)
        actual = self.header.pack[0]
        self.assertEqual(actual, expected)

    def test_add_header(self):
        expected = [('Content-Type', 'text/html'), ('Content-Length', '0')]
        self.header.add('Content-Length', '0')
        actual = self.header.pack[1]
        self.assertEqual(2, len(self.header.pack[1]))
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
