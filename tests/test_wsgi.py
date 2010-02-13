import unittest
import os.path
from pykaboo.pyka import Request, Response, Header, Wsgi, App
from pykaboo.pyka import RouteNotFoundException, AppNotFoundException, AppMethodNotFoundException

class TestApp(App):
    def get(self):
        return 'test app response'

class TestWsgi(unittest.TestCase):
    """
        test Wsgi methods except for __call__
    """
    def setUp(self):
        environ_get = {
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

        self.request = Request(environ_get)
        self.response = Response(self.request)
        self.routes = (
        "/__a__Content",
        "/content__a__Content",
        "/test__a__Test",
        "/foo/[a-z]{3}__a__Foo",
        "/spam/\w{3}/\w{3}__a__Foo",
        "/mia__mia__Mia")
        self.app_path = "/home/erick/labs/py/pykaboo/apps"
        self.wsgi = Wsgi(self.routes, os.path.realpath(os.path.dirname(__file__)), os.path.realpath(os.path.dirname(__file__)))

    def test_ok_get_route(self):
        path_info = '/'
        module, cls = self.wsgi.get_route(path_info)
        self.assertEqual(module, 'a')
        self.assertEqual(cls, 'Content')
        path_info = '/foo/bar'
        module, cls = self.wsgi.get_route(path_info)
        self.assertEqual(module, 'a')
        self.assertEqual(cls, 'Foo')
        path_info = '/spam/f21/f22'
        module, cls = self.wsgi.get_route(path_info)
        self.assertEqual(module, 'a')
        self.assertEqual(cls, 'Foo')

    def test_exception_route_not_found(self):
        path_info = '/foo/notfound'
        self.assertRaises(RouteNotFoundException, self.wsgi.get_route, path_info)

    def test_get_app(self):
        module, cls = 'test_wsgi', 'TestApp'
        app_instance = self.wsgi.get_app(module, cls, self.request, self.response)
        self.assertEqual(app_instance.__module__, module)
        self.assertTrue(app_instance.__class__.__name__, cls)

    def test_exception_app_not_found(self):
        module, cls = 'non_existent_module', 'Content'
        self.assertRaises(AppNotFoundException, self.wsgi.get_app, module, cls, self.request, self.response)
        module, cls = 'a', 'Non_existent_class'
        self.assertRaises(AppNotFoundException, self.wsgi.get_app, module, cls, self.request, self.response)

    def test_render_app_method(self):
        test_app = TestApp(self.request, self.response)
        render = self.wsgi.render_app_method(test_app, 'get')
        self.assertEquals(render, test_app.get())

    def test_exception_app_method_not_found(self):
        test_app = TestApp(self.request, self.response)
        self.assertRaises(AppMethodNotFoundException, self.wsgi.render_app_method, test_app, 'post')

