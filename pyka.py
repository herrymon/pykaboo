"""
desc:
an attempt at a tiny wsgi framework, 
status: usable

inspired by:
Ian Bicking tutorial - http://pythonpaste.org/webob/do-it-yourself.html, 
codepoint tutorial - http://webpython.codepoint.net/wsgi_tutorial

concepts, ideas borrowed from:
webob - http://bitbucket.org/ianb/webob/ 
werkzeug - http://werkzeug.pocoo.org/
bottle.py - http://github.com/defnull/bottle.
web.py - http://webpy.org/
pylons -http://pylonshq.com/ 
django - http://www.djangoproject.com

bookmarks:
http1.1 - http://www.w3.org/Protocols/rfc2616/rfc2616.html
PEP 333 - http://www.python.org/dev/peps/pep-0333/ 
wsgiref module, (wsgiref.validate) - http://docs.python.org/library/wsgiref.html
cgi module - http://docs.python.org/library/cgi.html
urlparse module - http://docs.python.org/library/urlparse.html 
Cookie module - http://docs.python.org/library/cookie.html 

notes:
dev runs on python 2.6.4, 
apache with mod_wsgi/wsgiref.simple_server
requires python 2.5
""" 

__version__ = '0.1'
__author__ = 'herrymonster@gmail.com'
__license__ = 'do whatever you want, Ie use at your own risk'

import os, sys, cgi
sys.path.append(os.path.dirname(__file__))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
import config

'''errors and logger'''
class HTTPRequestException(Exception): pass
class TemplateNotFoundException(Exception): pass
class RouteNotFoundException(Exception): pass
class AppNotFoundException(Exception): pass
class AppMethodNotFoundException(Exception): pass
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

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            # @see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi 
            exc_info = sys.exc_info()
            if exc_info[0].__name__ == RouteNotFoundException.__name__:
                header, message = self.error_404(exc_info)
            else:
                header, message = self.error_500(exc_info)
            start_response(header, [('Content-Type', 'text/html')], exc_info)
            return ErrorMiddleware.TEMPLATE.format(body=message, title=header)

    def error_404(self, exc_info):
            return "404 NOT FOUND", "<h1>404 Not Found</h1><pre>{msg}</pre>".format(msg=exc_info[1])

    def error_500(self, exc_info):
            from traceback import format_tb
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(exc_info[2])
            traceback.append('%s: %s' % (exc_info[0].__name__, exc_info[1]))
            return "500 INTERNAL SERVER ERROR", "<h1>500 Internal Server Error</h1><pre>{tb}</pre>".format(tb='<br/>'.join(traceback))


class LoggingMiddleware(object):
    """
        wsgi middleware to display at bottom of webpage, environ info
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        pass

if config.LOG:
    def log(msg):
        from datetime import datetime
        import logging
        now = datetime.now()
        log_filename = 'log-{year}-{month}-{day}.log'.format(year=now.year, month=now.month, day=now.day)
        log_file = os.path.join(config.LOG_PATH, log_filename)
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        logging.debug(msg)
else:
    def log(msg): 
        msg = None


#utility functions
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
    log('xutils.dictify: %d %s' %(len(input_text), input_text))
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
    tpaths = template_paths if template_paths else [config.TEMPLATES_PATH]
    mpath = module_path if module_path else os.path.join(config.PYKA_PATH, 'tmp')
    lookup = TemplateLookup(directories=tpaths, module_directory=mpath)
    template = lookup.get_template(template_name)
    return template.render(**kwargs)

def request(*args):
    """
        convenience wrapper for request object
    """

def response(*args):
    """
        convenience wrapper for response object
    """

# Database class
class Database(object):
    """
        a simple interface to rdbms, 
        supports only sqlite for now
        @requires python 2.5
    """
    def connect(self):
        '''returns a connection cursor'''
        if not config.DATABASE_DRIVER == 'sqlite3':
            raise DbNotSupportedException('only sqlite3 is supported for now')
        __import__(config.DATABASE_DRIVER)
        self.driver = sys.modules[config.DATABASE_DRIVER]
            
        conn = self.driver.connect(os.path.join(config.DATABASE_PATH, config.DATABASE_FILE))
        self.cursor = conn.cursor()

    def close(self):
        self.cursor.close()
        self.cursor = None

    def query(self, sql):
        self.connect()
        self.cursor.execute(sql)
        fetch = self.cursor.fetchall()
        self.close()
        return fetch


# main components
class Response(object):
    """
        wsgi Response, wraps a Request object,
        param for start_response
    """
    def __init__(self, request, ctype=None):
        self.request = request
        self.body = []
        # add default headers
        if ctype:
            self.header = Header('200 OK', ('Content-Type', ctype))
        else:
            self.header = Header('200 OK', ('Content-Type', 'text/html'))
            
    def show(self, *args):
        if self.request.method == 'HEAD':
            return ""
        else:
            for response in args:
                self.body.append(response)
            return "".join(self.body)


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
        self.cookie = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))
        for key in self.environ:
            log('{k} -> {v}'.format(k=key, v=str(self.environ[key])))
        log(self.debug)

    # on __init__ , wsgi.input must be read/cached, 
    # otherwise I'm getting empty wsgi.input
    def _post_cache(self):
        """cache content of wsgi.input on __init__"""
        from cStringIO import StringIO
        self.post_cache = StringIO('')
        if self.environ.get('REQUEST_METHOD') == 'POST':
            if self.environ.get('wsgi.input', None):
                self.post_cache = StringIO(self.environ['wsgi.input'].read(int(self.content_length)))
                self.form = cgi.FieldStorage(fp=self.post_cache, environ=self.environ, keep_blank_values=True)

    @property
    def base_url(self):
        return "{scheme}://{host}{script}/".format(
                    scheme=self.environ.get('wsgi.url_scheme'),
                    host=self.environ.get('HTTP_HOST'),
                    script=self.environ.get('SCRIPT_NAME','')
                )

    @property
    def method(self):
        supported_methods = ('GET', 'POST')
        method = self.environ.get('REQUEST_METHOD', 'GET')
        if method in supported_methods:
            return method.lower() # why lower? need to map this later to App method Eg def get(self)...
        else:
            raise HTTPRequestException('method is not supported. Only GET and POST is supported at the moment...')

    @property
    def path(self):
        # remove falsy values
        return [p for p in self.path_info.split('/') if p]

    @property
    def post(self):
        if self.environ.get('wsgi.input',None):
            return self.form
        else:
            return None
        #return cgi.FieldStorage(self.post_cache)

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
            base_url: {base}
            method: {meth}
            cookie: {cook} 
            path_info: {pi}
            path: {pth}""".format(
                            base=self.base_url, meth=self.method, 
                            cook=str(self.cookie), pi=self.path_info, 
                            pth=str(self.path)
        ) 

    def cookie_set(self, key, val, default, add_to=None, **kwargs):
        '''if COOKIE[key] exists set COOKIE[key] to val, else COOKIE[key] = default'''
        has_cookie = self.cookie.get(key, None)
        attributes = {'path':'/'}
        attributes.update(kwargs)
        is_number = isinstance(val, int)
        if has_cookie:
            if add_to:
                # to support int increment, for now
                if is_number:
                    self.cookie[key] = int(self.cookie[key].coded_value) + val
            else:
                self.cookie[key] = val
        else:
            self.cookie[key] = default
        for attr in attributes:
            self.cookie[key][attr] = attributes[attr]


class Template(object):
    """
        instantiate with filename of html template file. Do not forget to set TEMPLATE_PATH in config.py. 
        wrapper for string.Template @see http://docs.python.org/library/string.html#template-strings
    """
    def __init__(self, tfile, echo=True):
        try:
            self.echo = echo
            tpl = os.path.join(config.TEMPLATES_PATH, tfile)
            fp = open(tpl)
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


class App(object):
    """
        All apps inherit App. Do not forget to set APP_PATH in config.py
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

    @property
    def POST(self):
        return self.request.post

    @property
    def QUERY_STRING(self):
        return self.request.query_string

    def redirect(self, url_append, code=None):
        code = '303 SEE OTHER' if not code else code
        self.response.header.state(code)
        self.response.header.add('Location', self.request.base_url + url_append)


class Header(object):
    """
        status object and response headers packed to use as arg to start_response()
    """
    def __init__(self, _status, _header):
        '''@usage start_response(*header.pack)'''
        self.pack = []
        self.pack.append(_status)
        self.pack.append([_header])
        log('Header: Created header[status=%s, header=[%s]]' %(self.pack[0], str(self.pack[1])) )

    def state(self, _status):
        """usage header.state('404 NOT FOUND')"""
        self.pack[0] = _status

    def add(self, *args):
        """usage header.add('Content-Type', 'text/html')"""
        if args:
            self.pack[1].append(args)

    def add_cookie(self, cookie):
        for key in cookie:
            self.add('Set-Cookie', cookie[key].OutputString())


class Wsgi(object):
    """
        wsgi application wrapper
    """
    def __call__(self, environ, start_response):
        request = Request(environ)
        response = Response(request)

        module, cls = self.get_route(request.path_info, config.ROUTES)
        app = self.get_app(module, cls, request, response, config.APP_PATH)
        response_echo = response.show(self.render_app_method(app, request.method))
        response.header.add_cookie(request.cookie)

        start_response(*response.header.pack[:2])
        return response_echo
                
    def get_route(self, path_info, routes):
        import re
        for route in routes:
            url, module, cls = route.split('__')
            pattern = re.compile('^{0}$'.format(url)) #must be exact begin-to-end
            if re.match(pattern, path_info):
                return (module, cls)
        else:
            raise RouteNotFoundException('No route found, check that {0} matches with ROUTE'.format(path_info))

    def get_app(self, module, cls, request, response, app_path):
        """
            create an app object 
            NOTES:
            @see http://technogeek.org/python-module.html 
            @see http://docs.python.org/library/functions.html#__import__
        """
        app_exists = lambda m: os.path.isfile( os.path.join(app_path, '{0}.{1}'.format(m, 'py')) )

        if not app_exists(module):
            raise AppNotFoundException('App module {0} not found in APP_PATH {1}'.format(module, app_path))
        else:
            sys.path.append(app_path)
            try:
                __import__(module)
                app_module = sys.modules[module]
                app_cls = getattr(app_module, cls)
            except ImportError:
                raise AppNotFoundException('App module {0} not found in APP_PATH {1}'.format(module, app_path))
            except AttributeError:
                raise AppNotFoundException('App class {0} not found in module {1}'.format(cls, module))
            return app_cls(request, response)

    def render_app_method(self, app, method):
        try:
            app_method = getattr(app, method)
        except AttributeError:
            raise AppMethodNotFoundException('App class {0} has no method {1}'.format(app.__class__.__name__, method))
        return app_method()


application = ErrorMiddleware(Wsgi())

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    try:
        httpd = make_server('', 8888, application)
        print "Serving on port 8888\nCtrl + C to quit"
        httpd.serve_forever()
    except KeyboardInterrupt:
        print "\nShutting down server on port 88888"

