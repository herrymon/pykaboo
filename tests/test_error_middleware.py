import unittest
from pykaboo.pyka import ErrorMiddleware, Wsgi

def app(environ, start_response):
    start_response('200 OK', [('Content-type','text/plain')])
    return ['Hello, world']

class TestErrorMiddleware(unittest.TestCase):
    """
        test generation of 500 and 404 responses
    """
    def setup(self):
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
