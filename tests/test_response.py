import unittest
from pykaboo.pyka import Response, Request

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
        expected = '200 OK'
        self.assertEqual(expected, self.response.status)
        expected = [('Content-Type', 'text/html; charset=UTF-8')]
        self.assertEqual(expected, self.response.header)

    def test_init_body(self):
        actual = self.response.body
        expected = ''
        self.assertEqual(actual, expected)

    def test_change_body(self):
        expected = ('test changing the response body', 'add another')
        self.response.add(expected[0])
        self.assertEqual(self.response.body, expected[0])
        self.response.add(expected[1])
        self.assertEqual(self.response.body, ''.join(expected))

if __name__ == '__main__':
    unittest.main()
