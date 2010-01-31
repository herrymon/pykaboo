import __init__
import unittest
from pykaboo.pyka import Response
from pykaboo.pyka import Request
from pykaboo.pyka import Header

class TestResponseAttributes(unittest.TestCase):
    """
        test if response set default attributes as intended
    """
    def setUp(self):
        self.environ = {
            'CONTENT_LENGTH': '0',
            'PATH_INFO': '',
            'HTTP_COOKIE': '',
            'REQUEST_METHOD': 'GET',
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'localhost',
            'SCRIPT_NAME': '',
            'QUERY_STRING': ''
        }
        request = Request(self.environ)
        self.response = Response(request)

    def test_init_headers(self):
        actual = self.response.header
        expected = Header('200 OK', ('Content-Type','text/html'))
        self.assertEqual(actual.pack, expected.pack)

    def test_init_request(self):
        request = Request(self.environ)
        actual = self.response.request.environ
        self.assertEqual(actual, request.environ)

    def test_init_output(self):
        actual = self.response.output
        expected = []
        self.assertEqual(actual, expected)

    def test_change_output(self):
        expected = 'test changing the response output'
        actual = self.response.show(expected)
        self.assertEqual(self.response.output, [expected])
        self.assertEqual(actual, expected)
        self.response.show('add another output')
        self.assertEqual(2, len(self.response.output))

    def test_add_coookie_header(self):
        from Cookie import SimpleCookie
        c = SimpleCookie()
        c['test'] = 'foobar'
        c['spam'] = 'egg'
        self.response.cookie_header(c, ['test', 'spam'])
        actual = self.response.header
        expected = Header('200 OK', ('Content-Type','text/html'))
        expected.add('Set-Cookie','test=foobar')
        expected.add('Set-Cookie','spam=egg')
        self.assertEquals(actual.pack, expected.pack)

if __name__ == '__main__':
    unittest.main()
