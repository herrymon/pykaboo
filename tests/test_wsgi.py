import unittest
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
        "/foo__a__Foo",
        "/mia__mia__Mia")
        self.app_path = "/home/erick/labs/py/pykaboo/apps"

    def test_ok_get_route(self):
        wsgi = Wsgi()
        path_info = '/'
        module, cls = wsgi.get_route(path_info, self.routes)
        self.assertEqual(module, 'a')
        self.assertEqual(cls, 'Content')
        path_info = '/foo'
        module, cls = wsgi.get_route(path_info, self.routes)
        self.assertEqual(module, 'a')
        self.assertEqual(cls, 'Foo')

    def test_exception_route_not_found(self):
        wsgi = Wsgi()
        path_info = '/notfound'
        self.assertRaises(RouteNotFoundException, wsgi.get_route, path_info, self.routes)

    def test_get_app(self):
        wsgi = Wsgi()
        module, cls = 'a', 'Content'
        app_instance = wsgi.get_app(module, cls, self.request, self.response, self.app_path)
        self.assertEqual(app_instance.__module__, module)
        self.assertTrue(app_instance.__class__.__name__, cls)

    def test_exception_app_not_found(self):
        wsgi = Wsgi()
        module, cls = 'non_existent_module', 'Content'
        self.assertRaises(AppNotFoundException, wsgi.get_app, module, cls, self.request, self.response, self.app_path)
        module, cls = 'a', 'Non_existent_class'
        self.assertRaises(AppNotFoundException, wsgi.get_app, module, cls, self.request, self.response, self.app_path)

    def test_render_app_method(self):
        wsgi = Wsgi()
        test_app = TestApp(self.request, self.response)
        render = wsgi.render_app_method(test_app, 'get')
        self.assertEquals(render, test_app.get())

    def test_exception_app_method_not_found(self):
        wsgi = Wsgi()
        test_app = TestApp(self.request, self.response)
        self.assertRaises(AppMethodNotFoundException, wsgi.render_app_method, test_app, 'post')

