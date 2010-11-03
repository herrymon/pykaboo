"""
desc:
a python newbies attempt at a one-file wsgi framework
status: usable but not great

inspired by:
Ian Bicking tutorial - http://pythonpaste.org/webob/do-it-yourself.html, 
codepoint tutorial - http://webpython.codepoint.net/wsgi_tutorial

concepts, ideas borrowed from:
webob - http://bitbucket.org/ianb/webob/ 
werkzeug - http://werkzeug.pocoo.org/
bottle.py - http://github.com/defnull/bottle.
bobo - http://bobo.digicool.com/ 

bookmarks:
http1.1 - http://www.w3.org/Protocols/rfc2616/rfc2616.html
PEP 333 - http://www.python.org/dev/peps/pep-0333/ 
wsgiref module, (wsgiref.validate) - http://docs.python.org/library/wsgiref.html
cgi module - http://docs.python.org/library/cgi.html
urlparse module - http://docs.python.org/library/urlparse.html 
Cookie module - http://docs.python.org/library/cookie.html 

notes:
dev runs on python 2.6.4, 
so far I have only tried deploying it via apache with mod_wsgi
wsgiref.simple_server (for dev)
requires python 2.6
""" 

__version__ = '0.1'
__author__ = 'herrymonster@gmail.com'
__license__ = 'do whatever you want, Ie use at your own risk'
__all__ = ['application', 'get', 'post', 'xget', 'xpost', 'Request', 'Response', 'mako_render']

import os, sys, cgi
from collections import namedtuple
PYKA_PATH = os.path.realpath(os.path.dirname(__file__))
# sys.path.append(os.path.dirname(__file__))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango

'''errors and logger'''
class UnknownHTTPMethod(Exception): pass
class InvalidHTTPMethod(Exception): pass
class PostFieldNotFound(Exception): pass
class TemplateNotFoundException(Exception): pass
class RouteNotFound(Exception): pass
class NotXHR(Exception): pass
class DbNotSupportedException(Exception): pass

class ErrorMiddleware(object):
    """
        wsgi middleware to handle exceptions in wsgi app
        via pylonsbook @see http://pylonsbook.com/en/1.1/the-web-server-gateway-interface-wsgi.html#handling-errors
    """
    TEMPLATE = """
            <html>
            <head>
            <style>pre{{background:#def;border:1px solid #cde;margin:1em;padding:0.75em}}</style>
            </head>
            <title>{title}</title>
            <body>
            {body}
            </body>
            </html>
    """
    def __init__(self, app):
        self.app = app
        self.handlers = app.handlers

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            # @see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi 
            exc_info = sys.exc_info()
            if exc_info[0].__name__ == RouteNotFound.__name__:
                header, message = self.error_404(exc_info)
            else:
                header, message = self.error_500(exc_info)
            start_response(header, [('Content-Type', 'text/html; charset=UTF-8')], exc_info)
            return ErrorMiddleware.TEMPLATE.format(body=message, title=header)

    def error_404(self, exc_info):
            return "404 NOT FOUND", "<h1>404 Not Found</h1><pre>{msg}</pre>".format(msg=exc_info[1])

    def error_500(self, exc_info):
            from traceback import format_tb
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(exc_info[2])
            traceback.append('%s: %s' % (exc_info[0].__name__, exc_info[1]))
            return "500 INTERNAL SERVER ERROR", "<h1>500 Internal Server Error</h1><pre>{tb}</pre>".format(tb='<br/>'.join(traceback))


#utility functions
def log(msg, logtype=None):
    from datetime import datetime
    import logging
    now = datetime.now()
    log_filename = 'log-{0.year}-{0.month}-{0.day}.log'.format(now)
    log_path = os.path.join(PYKA_PATH, 'log')
    log_file = os.path.join(log_path, log_filename)
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    log_fn = {None: logging.info, 'debug': logging.debug, 'warning': logging.warning, 'error': logging.error, 'critical': logging.critical}
    log_fn[logtype]('{0.hour:2}:{0.minute:2} {1}'.format(now, msg))

def expires_in(**kwargs):
    """returns a string date, for cookie 'expires' attribute
    @see rf2109 10.1.2"""
    from time import time, gmtime, strftime
    total_secs = (
        kwargs.pop('day', 0) * 24 * 60 * 60,
        kwargs.pop('hour', 0) * 60 * 60,
        kwargs.pop('min', 0) * 60,
        kwargs.pop('sec', 0)
    )
    expiry_time = gmtime(kwargs.pop('time', time()) + sum(total_secs))
    return strftime('%a, %d-%b-%Y %H:%M:%S GMT', expiry_time)

def dictify(input_text, escape=True):
    """
        convert wsgi.input to {}, uses built-in urlparse module
        Eg name=Erick&pets=rat&pets=cats to {'name': ['Erick'], 'pets': ['rats', 'cats']}
        Note: all values are lists
    """
    log('xutils.dictify: {0} {1}'.format(len(input_text), input_text))
    from urlparse import parse_qs
    dict_input = parse_qs(input_text)
    # use cgi.escape built-in to escape "&<>" input_text 
    if escape:
        for key in dict_input:
            dict_input[key] = [cgi.escape(val) for val in dict_input[key]]
    return dict_input

def mako_render(template_name, template_paths=None, module_path=None, **kwargs):
    """
        wrap mako.TemplateLookup.get_template and mako.Template.render
        @see http://www.makotemplates.org/
    """
    from mako.template import Template
    from mako.lookup import TemplateLookup
    if template_paths:
        tpath = template_paths
    else:
        tpath = [PYKA_PATH]
    if module_path:
        mpath = module_path
    else:
        mpath = os.path.join(PYKA_PATH, 'tmp')
    lookup = TemplateLookup(directories=tpath, module_directory=mpath)
    template = lookup.get_template(template_name)
    return template.render(**kwargs)


# 
class Database(object):
    """
        a simple interface to rdbms, 
        tested only with sqlite3
        @requires python 2.5
    """
    def connect(self, db_driver, db_file):
        '''returns a connection cursor'''
        try:
            __import__(db_driver)
            self.driver = sys.modules[db_driver]
        except ImportError:
            raise DbNotSupportedException('only sqlite3 is supported for now')
            
        conn = self.driver.connect(db_file)
        self.cursor = conn.cursor()

    def close(self):
        self.cursor.close()
        self.cursor = None

    def query(self, sql, db_file, sql_params=None, db_driver='sqlite3'):
        self.connect(db_driver, db_file)
        if sql_params:
            self.cursor.execute(sql, sql_params)
        else:
            self.cursor.execute(sql)
        fetch = self.cursor.fetchall()
        self.close()
        return fetch


# main components
class Response(object):
    """
        wsgi Response, has a Request object attribute,
    """
    def __init__(self, request, ctype=None):
        self.__request = request
        if ctype:
            self.__ctype = ctype
        else:
            self.__ctype = 'text/html; charset=UTF-8'
        self.__body = []
        from Cookie import SimpleCookie
        self.__cookie = SimpleCookie()
        # add default headers
        self.__header = ('200 OK', [('Content-Type', self.__ctype)])

    @property
    def body(self):
        if self.__request.method == 'HEAD':
            return ""
        else:
            return "".join(self.__body)
            
    @property
    def status(self):
        return self.__header[0]

    @property
    def header(self):
        return self.__header[1]

    def add(self, *args):
        from types import StringTypes, FunctionType
        for response in args:
            if type(response) is FunctionType:
                self.add(response())
            if type(response) is StringTypes:
                self.__body.append(response)
            else:
                self.__body.append(str(response))

    def cookie(self, key, value):
        """
           add Set-Cookie headers
        """
        self.__cookie[key] = value
        self.__cookie[key]['path'] = '/'
        for key in self.__cookie.iterkeys():
            self.__header[1].append(('Set-Cookie', self.__cookie[key].OutputString()))

    def redirect(self, url_append, code=None):
        if not code:
            code = '303 SEE OTHER'
        self.response.header.state(code)
        self.response.header.add('Location', self.__request.base_url + url_append)



class Request(object):
    """
        container of WSGI environ object
    """
    def __init__(self, environ):
        self.environ = environ
        self.content_length = self.environ.get('CONTENT_LENGTH', '0')
        self.path_info = self.environ.get('PATH_INFO', '')
        self._post_cache()
        from Cookie import SimpleCookie
        self.cookie_cache = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))
        for key in self.environ.iterkeys():
            log('{0}: {1!s}'.format(key, self.environ[key]))
        log(self.debug)

    # on __init__ , wsgi.input must be read/cached, 
    # otherwise I'm getting empty wsgi.input
    def _post_cache(self):
        """cache content of wsgi.input on __init__"""
        from cStringIO import StringIO
        self.post_cache = StringIO('')
        if self.environ.get('REQUEST_METHOD') == 'POST':
            wsgi_input = self.environ.get('wsgi.input', None)
            if wsgi_input:
                self.post_cache = StringIO(wsgi_input.read(int(self.content_length)))
                self.form = cgi.FieldStorage(fp=self.post_cache, environ=self.environ, keep_blank_values=True)

    @property
    def base_url(self):
        return "{scheme}://{host}{script}/".format(
                    scheme=self.environ.get('wsgi.url_scheme'),
                    host=self.environ.get('HTTP_HOST', ''),
                    script=self.environ.get('SCRIPT_NAME','')
                )
    @property
    def http_host(self):
        return self.environ.get('HTTP_HOST', '')

    @property
    def method(self):
        supported_methods = ('GET', 'POST')
        method = self.environ.get('REQUEST_METHOD', 'GET')
        if method in supported_methods:
            return method
        else:
            raise UnknownHTTPMethod('method is not supported. Only GET and POST is supported at the moment...')

    @property
    def path(self):
        # remove falsy values
        return [p for p in self.path_info.split('/') if p]

    def post(self, field):
        if self.method != 'POST':
            raise InvalidHTTPMethod('There are no fields to access, request should be POST')
        if self.form:
            value = self.form.getvalue(field)
            if not value:
                raise PostFieldNotFound('no value POSTed for {0}'.format(field))
            else:
                return value

    @property
    def query_string(self):
        return dictify(self.environ.get('QUERY_STRING',''))

    @property
    def referrer(self):
        return self.environ.get('HTTP_REFERRER','')
        
    @property
    def debug(self):
        """string representation of Request attributes"""
        return """
            base_url: {0.base_url}
            method: {0.method}
            cookie_cache: {0.cookie_cache} 
            path_info: {0.path_info}
            path: {0.path}
            is_xhr: {1}""".format(self, self.is_xhr())

    def cookie(self, key):
        c = self.cookie_cache.get(key, None)
        if c:
            return self.cookie_cache[key].value
        else:
            return ''

    def is_xhr(self):
        """
        copied from webob request class @url http://bitbucket.org/ianb/webob/src/tip/webob/request.py 
        Note: not all ajax requests will have HTTP_X_REQUESTED_WITH http header
        """
        return self.environ.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest'


class Template(object):
    """
        instantiate with filename of html template file
        wrapper for string.Template @see http://docs.python.org/library/string.html#template-strings
    """
    def __init__(self, tfile, tpath=None, echo=True):
        if not tpath:
            tpath = PYKA_PATH
        try:
            self.echo = echo
            tpl = os.path.join(tpath, tfile)
            fp = open(tpl, 'rt', encoding='utf-8')
            self.html = fp.read()
            fp.close()
        except IOError:
            raise TemplateNotFoundException('Template file not found: %s' %tpl)
            
    def render(self, values={}):
        from string import Template
        t = Template(self.html)
        try:
            for key in values:
                cgi.escape(values[key])
            page = t.substitute(values)
        except KeyError:
            log('Template: Template key errors: %s' %str(values))
            self.html = 'Template key errors: %s' %str(values)
            page = 'Template key errors'
        return page


# keys for handler_func in class Wsgi
HandlerKey = namedtuple('HandlerKey', ['path', 'method', 'is_xhr'])

class Wsgi(object):
    """
        wsgi application wrapper
    """
    def __init__(self, file_path=None):
        self.handlers = {} 

    def __call__(self, environ, start_response):
        # get request, extra attribute, self.method, a copy of request.method for convenience
        self.request = Request(environ)
        self.method = self.request.method
        response = Response(self.request)
        
        # if self.route() does not find a handler or catches error in trying to find a handler, this request is dead, 
        # maybe add another if None check??? overkill?!?

        handler_func = self.handlers.get(self.route(), None)
        handler_func.request = self.request
        handler_func.response = response
        response.add(handler_func)

        start_response(response.status, response.header)
        return response.body
                
    def route(self):
        from re import compile, search
        for route in self.handlers.iterkeys():
            pattern = compile('^{0}$'.format(route.path)) #must be exact match begin-to-end
            if search(pattern, self.request.path_info): # check if path_info matches a route, routes method matches the handler method
                if route.method == self.method:
                    if route.is_xhr == self.request.is_xhr():
                        return route
                    else:
                        raise NotXHR('Expecting HTTP_X_REQUESTED_WITH header, but found nothing, zero, zip, nil')
                else:
                    raise InvalidHTTPMethod('Expecting HTTP method {0}, found {1}'.format(route.method, self.method))
        else:
            raise RouteNotFound("No handler found for route: {0}".format(self.request.path_info))
            

application = ErrorMiddleware(Wsgi()) # wrap it in middleware so we can have more usefull error message 
                                      # and some html formatting for 404 and 500

def bind(route, app, method, is_xhr=False):
    """
        decorator function
        add handler mapping to Wsgi instance
        { HandlerKey : handler_func }
    """
    def decor(fn):
        app.handlers[HandlerKey(route, method, is_xhr)] = fn
        return fn
    return decor

def post(route):
    return bind(route, application, 'POST')

def get(route):
    return bind(route, application, 'GET')

def xget(route):
    return bind(route, application, 'GET', is_xhr=True)

def xpost(route):
    return bind(route, application, 'POST', is_xhr=True)

def serve(application, port=8080):
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('', port, application)
        print "Serving on port {0}\nCtrl + C to quit".format(port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "\nShutting down server on port {0}".format(port)

#end of pyka.py
