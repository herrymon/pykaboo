import unittest
import os.path
from pykaboo.pyka import Request, Response, Wsgi, bind, HandlerKey
from pykaboo.pyka import RouteNotFound

# sample app
def index():
    return 'index'

def test():
    return 'test'


class TestWsgi(unittest.TestCase):
    """
        test Wsgi methods except for __call__
    """
    def setUp(self):
        self.environ = {
            'CONTENT_LENGTH': '0',
            'PATH_INFO': '/',
            'HTTP_COOKIE': '',
            'REQUEST_METHOD': 'GET',
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'localhost',
            'HTTP_COOKIE': '',
            'SCRIPT_NAME': '',
            'QUERY_STRING': ''
        }

        self.request = Request(self.environ)
        self.response = Response(self.request)
        self.wsgi = Wsgi()

        self.wsgi.handlers = {HandlerKey('/','GET'): index, HandlerKey('/test','GET'): test}
        self.wsgi.method = 'GET'

    def test_ok_get_route(self):
        path_info = '/'
        self.assertEquals(self.wsgi.route(path_info), HandlerKey('/','GET'))
        path_info = '/test'
        self.assertEquals(self.wsgi.route(path_info), HandlerKey('/test','GET'))

    def test_raises_route_not_found(self):
        path_info = '/notfound'
        self.assertRaises(RouteNotFound, self.wsgi.route, path_info)

