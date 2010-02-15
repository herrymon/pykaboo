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
        actual = self.header.status
        expected = '200 OK'
        self.assertEqual(actual, expected)

    def test_init_headers(self):
        actual = self.header.headers
        expected = [('Content-Type', 'text/html')]
        self.assertEqual(actual, expected)

    def test_change_state(self):
        expected = '404 NOT FOUND'
        self.header.state(expected)
        actual = self.header.status
        self.assertEqual(actual, expected)

    def test_add_header(self):
        expected = [('Content-Type', 'text/html'), ('Content-Length', '0')]
        self.header.add('Content-Length', '0')
        actual = self.header.headers
        self.assertEqual(2, len(actual))
        self.assertEqual(actual, expected)

    def test_add_cookie_header(self):
        expected = [('Content-Type', 'text/html'), ('Set-Cookie', 'test=foobar; Path=/'), ('Set-Cookie', 'spam=egg')]
        from Cookie import SimpleCookie
        cookie = SimpleCookie()
        cookie['test'] = 'foobar'
        cookie['test']['path'] = '/'
        cookie['spam'] = 'egg'
        self.header.add_cookie(cookie)
        actual = self.header.headers
        self.assertEqual(3, len(actual))
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
