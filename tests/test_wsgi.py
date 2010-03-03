import unittest
import os.path
from pykaboo.pyka import Request, Response, Wsgi, bind, HandlerKey
from pykaboo.pyka import RouteNotFound, NotXHR

# sample app
def index(): pass
def test(): pass
def xtest(): pass


class TestWsgi(unittest.TestCase):
    """
        test Wsgi methods except for __call__
    """
    def setUp(self):
        environs = (
            {
                'CONTENT_LENGTH': '0',
                'PATH_INFO': '/',
                'HTTP_COOKIE': '',
                'REQUEST_METHOD': 'GET',
                'wsgi.url_scheme': 'http',
                'HTTP_HOST': 'localhost',
                'HTTP_COOKIE': '',
                'SCRIPT_NAME': '',
                'QUERY_STRING': ''
            },
            {
                'CONTENT_LENGTH': '0',
                'PATH_INFO': '/test',
                'HTTP_COOKIE': '',
                'REQUEST_METHOD': 'GET',
                'wsgi.url_scheme': 'http',
                'HTTP_HOST': 'localhost',
                'HTTP_COOKIE': '',
                'SCRIPT_NAME': '',
                'QUERY_STRING': ''
            },
            {
                'CONTENT_LENGTH': '0',
                'PATH_INFO': '/xtest',
                'HTTP_COOKIE': '',
                'REQUEST_METHOD': 'GET',
                'wsgi.url_scheme': 'http',
                'HTTP_HOST': 'localhost',
                'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
                'HTTP_COOKIE': '',
                'SCRIPT_NAME': '',
                'QUERY_STRING': ''
            },
            {
                'CONTENT_LENGTH': '0',
                'PATH_INFO': '/nohandler',
                'HTTP_COOKIE': '',
                'REQUEST_METHOD': 'GET',
                'wsgi.url_scheme': 'http',
                'HTTP_HOST': 'localhost',
                'HTTP_COOKIE': '',
                'SCRIPT_NAME': '',
                'QUERY_STRING': ''
            }
        )

        self.requests = [Request(e)  for e in environs]
        self.wsgi = Wsgi()
        self.wsgi.handlers = {
                HandlerKey('/','GET', False): index, 
                HandlerKey('/test', 'GET', False): test,
                HandlerKey('/xtest', 'GET', True): xtest
                }

    def test_ok_get_route(self):
        self.wsgi.request = self.requests[0]
        self.wsgi.method = 'GET'
        self.assertEquals(self.wsgi.route(), HandlerKey('/', 'GET', False))
        self.wsgi.request = self.requests[1]
        self.wsgi.method = 'GET'
        self.assertEquals(self.wsgi.route(), HandlerKey('/test', 'GET', False))

    def test_ok_xget_route(self):
        self.wsgi.request = self.requests[2]
        self.wsgi.method = 'GET'
        self.assertEquals(self.wsgi.route(), HandlerKey('/xtest', 'GET', True))

    def test_raises_route_not_found(self):
        self.wsgi.request = self.requests[3]
        self.wsgi.method = 'GET'
        self.assertRaises(RouteNotFound, self.wsgi.route)

    def test_raises_not_xhr(self):
        self.wsgi.request = self.requests[0]
        self.wsgi.method = 'GET'
        self.wsgi.handlers = { HandlerKey('/', 'GET', True): index }
        self.assertRaises(NotXHR, self.wsgi.route)

