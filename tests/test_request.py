import unittest
from cStringIO import StringIO
from pykaboo.pyka import Request
from pykaboo.pyka import UnknownHTTPMethod

class TestRequestAttributes(unittest.TestCase):
    """
        test if request instance sets default attributes as intended
    """
    def setUp(self):
        environ_get = {
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
        self.post_str = 'city=Manila&coffee=dark&colors=blue&colors=green'
        environ_post = {
            'CONTENT_LENGTH': len(self.post_str),
            'PATH_INFO': '/form',
            'HTTP_COOKIE': '',
            'REQUEST_METHOD': 'POST',
            'wsgi.url_scheme': 'http',
            'wsgi.input':StringIO(self.post_str),
            'HTTP_HOST': 'localhost',
            'HTTP_COOKIE': '',
            'SCRIPT_NAME': '',
            'QUERY_STRING': ''
        }
        self.request_get = Request(environ_get)
        self.request_post = Request(environ_post)

    def test_init_method(self):
        actual = self.request_get.method
        self.assertEqual(actual, 'get')
        actual = self.request_post.method
        self.assertEqual(actual, 'post')

    def test_init_base_url(self):
        actual = self.request_get.base_url
        self.assertEqual(actual, 'http://localhost/')
        actual = self.request_post.base_url
        self.assertEqual(actual, 'http://localhost/')

    def test_init_path(self):
        actual = self.request_get.path
        self.assertFalse(actual)
        self.assertEqual(actual, [])
        actual = self.request_post.path
        self.assertTrue(actual)
        self.assertEqual(actual, ['form'])

    def test_init_query_string(self):
        actual = self.request_get.query_string
        self.assertFalse(actual)
        self.assertEqual(actual, {})
        actual = self.request_post.query_string
        self.assertFalse(actual)
        self.assertEqual(actual, {})

    def test_init_post(self):
        actual = self.request_get.post
        self.assertFalse(actual)
        self.assertEqual(actual, None)
        actual = self.request_post.post
        self.assertTrue(actual)
        actual = self.request_post.post['city'].value
        self.assertEqual('Manila', actual)
        actual = self.request_post.post.getlist('colors')
        self.assertEqual(actual, ['blue','green'])

    def test_init_cookie(self):
        from Cookie import SimpleCookie
        expected = SimpleCookie('')
        actual = self.request_get.cookie
        self.assertEqual(actual, expected)
        actual = self.request_post.cookie
        self.assertEqual(actual, expected)

    def test_init_content_length(self):
        actual = self.request_get.content_length
        self.assertEqual(actual, '0')
        actual = self.request_post.content_length
        self.assertEqual(actual, len(self.post_str))

if __name__ == '__main__':
    unittest.main()
