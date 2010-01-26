import __init__
import unittest
from pykaboo.pyka import Request
from pykaboo.pyka import HTTPRequestException

class TestRequestAttributes(unittest.TestCase):
    """
        test if request instance sets default attributes as intended
    """
    def setUp(self):
        environ = {
            'CONTENT_LENGTH': '0',
            'PATH_INFO': '',
            'HTTP_COOKIE': '',
            'REQUEST_METHOD': 'GET',
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'localhost',
            'HTTP_COOKIE': '',
            'SCRIPT_NAME': '',
            'QUERY_STRING': ''
        }
        self.request = Request(environ)

    def test_init_method(self):
        actual = self.request.method
        self.assertEqual(actual, 'get')

    def test_init_base_url(self):
        actual = self.request.base_url
        self.assertEqual(actual, 'http://localhost/')

    def test_init_path(self):
        actual = self.request.path
        self.assertFalse(actual)
        self.assertEqual(actual, [])

    def test_init_query_string(self):
        actual = self.request.query_string
        self.assertFalse(actual)
        self.assertEqual(actual, {})

    def test_init_post(self):
        actual = self.request.post
        self.assertFalse(actual)
        self.assertEqual(actual, {})

    def test_init_cookie(self):
        from Cookie import SimpleCookie
        actual = self.request.cookie
        expected = SimpleCookie('')
        self.assertEqual(actual, expected)

    def test_init_content_length(self):
        actual = self.request.content_length
        self.assertEqual(actual, '0')

if __name__ == '__main__':
    unittest.main()
