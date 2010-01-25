'''
desc:
an attempt at a tiny wsgi framework, 
status: barely usable

inspired by:
Ian Bicking tutorial - http://pythonpaste.org/webob/do-it-yourself.html, 
codepoint tutorial - http://webpython.codepoint.net/wsgi_tutorial

concepts, ideas borrowed from:
webob - http://bitbucket.org/ianb/webob/ 
werkzeug - http://werkzeug.pocoo.org/
bottle.py - http://github.com/defnull/bottle.
web.py - http://webpy.org/
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
''' 

__version__ = '0.1'
__author__ = 'herrymonster@gmail.com'
__license__ = 'do whatever you want, Ie use at your own risk'

import os, sys
sys.path.append(os.path.dirname(__file__))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
import config

'''constants'''
EXT = '.py'

'''errors and logger'''
class HTTPRequestException(Exception): pass
class TemplateNotFoundException(Exception): pass

if config.LOG:
    def log(msg):
        from datetime import datetime
        import logging
        now = datetime.now()
        log_file = '{path}log-{year}-{month}-{day}.log'.format(path=config.LOG_PATH, year=now.year, month=now.month, day=now.day)
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        logging.debug(msg)
else:
    def log(msg): 
        msg = None


#utility functions
def dictify(input_text):
    """
    convert wsgi.input to {}, uses built-in urlparse module
    Eg name=Erick&pets=rat&pets=cats to {'name': ['Erick'], 'pets': ['rats', 'cats']}
    Note: all values are lists
"""
    log('xutils.dictify: %d %s' %(len(input_text), input_text))
    from urlparse import parse_qs
    from cgi import escape
    dict_input = parse_qs(input_text)
    # use cgi.escape built-in to escape "&<>" from GET and POST, or other inputs
    for key in dict_input:
        dict_input[key] = [escape(val) for val in dict_input[key]]
    return dict_input

def _404():
    '''no route found'''
    # @TODO put a Template here
    return 'Page not found'

# Database class
class Database(object):
    """
    a simple interface to rdbms, 
    supports only sqlite for now
"""
    def _connect(self):
        '''returns a connection cursor'''
        if config.DATABASE_DRIVER == 'sqlite':
            import sqlite3
            conn = sqlite3.connect(config.DATABASE)
            cursor = conn.cursor()
        return cursor

    def query(self, _query):
        cursor = self._connect()
        if config.DATABASE_DRIVER == 'sqlite':
            cursor.execute(_query)
            return cursor.fetchall()

#main components
class Response(object):
    """
    wsgi Response, wraps a Request object,
    use this for start_response
"""
    def __init__(self, _request):
        self.response = []
        self.request = _request
        # add default headers
        self.header = Header('200 OK', ('Content-Type', 'text/html'))

    def __call__(self, booger=None):
        if self.request.method == 'HEAD':
            return ''
        else:
            # red box that appears at bottom of page if config.DEBUG is True
            is_debug = booger and config.DEBUG
            if is_debug:
                booger.append('\nself.request.POST.keys()'+','.join(self.request.post.keys()))
                from cgi import escape
                self.add('<pre style="background:#fdd;border:1px solid #ecc;margin:0;padding:1em">')
                self.add('<h3 style="margin:0;padding:0.2em;line-height:1.5em;background:#800;color:#fff">config.DEBUG is on, turn off debugging to hide this box</h3>')
                for b in booger:
                    self.add([escape(b)])
                self.add('</pre>')
            _response = ''.join(self.response)
            return _response

    def add(self, resp=None):
        """add list to response output"""
        self.response.extend(resp)

    def cookie_header(self, cookie, keys):
        for key in keys:
            self.header.add('Set-Cookie', '{0}={1}'.format(key, cookie[key].value))



class Request(object):
    '''container of WSGI environ object'''
    def __init__(self, _env):
        self.environ = _env
        self.content_length = self.environ.get('CONTENT_LENGTH', '0')
        self.path_info = self.environ.get('PATH_INFO', '')
        self._post_cache()
        from Cookie import SimpleCookie
        self.cookie = SimpleCookie(self.environ.get('HTTP_COOKIE', ''))

    # on __init__ , wsgi.input must be read/cached, 
    # otherwise I'm getting empty wsgi.input
    def _post_cache(self):
        """cache content of wsgi.input on __init__"""
        self.post_cache = ''
        if self.environ.get('REQUEST_METHOD') == 'POST':
            if self.environ.get('wsgi.input',''):
                from cStringIO import StringIO
                body = StringIO(self.environ.get('wsgi.input').read(int(self.content_length)))
                self.post_cache = body.read()

    @property
    def base_url(self):
        url = []
        script = self.environ.get('SCRIPT_NAME','')
        url.append(self.environ.get('wsgi.url_scheme'))
        url.append('://')
        url.append(self.environ.get('HTTP_HOST'))
        url.append(script)
        url.append('/')
        return ''.join(url)

    @property
    def method(self):
        _supported_methods = ('GET', 'POST')
        _method = self.environ.get('REQUEST_METHOD', None)
        if _method and _method in _supported_methods:
            return _method.lower() # why lower? need to map this later to Controller method Eg def get(self)...
        else:
            raise HTTPRequestException('method is not supported. Only GET and POST is supported at the moment...')

    @property
    def path(self):
        # remove empty strings
        path = [p for p in self.path_info.split('/') if p]
        return path

    @property
    def post(self):
        return dictify(self.post_cache)

    @property
    def query_string(self):
        return dictify(self.environ.get('QUERY_STRING',''))
        
    @property
    def debug(self):
        """string representation of Request attributes"""
        return """
            base_url: {base}
            method: {meth}
            post: {post}
            query_string: {qs} 
            cookie: {cook} 
            path_info: {pi}
            path: {pth}""".format(
                            base=self.base_url, meth=self.method, 
                            post=str(self.post), qs=str(self.query_string), 
                            cook=str(self.cookie), pi=self.path_info, pth=str(self.path)
        ) 

    def cookie_set(self, key, val, default, add_to=None):
        '''if COOKIE[key] exists set COOKIE[key] to val, else COOKIE[key] = default'''
        has_cookie = self.cookie.get(key, None)
        is_number = isinstance(val, int)
        if has_cookie:
            if add_to:
                ''' to support int increment, for now'''
                if is_number:
                    self.cookie[key] = int(self.cookie[key].value) + val
            else:
                self.cookie[key] = val
        else:
            self.cookie[key] = default



class Template(object):
    """
    instantiate with filename of html template file. Do not forget to set TEMPLATE_PATH in config.py. 
    wrapper for string.Template @see http://docs.python.org/library/string.html#template-strings
"""
    def __init__(self, tfile, echo=True):
        try:
            self.echo = echo
            tpl = config.TEMPLATES_PATH + tfile
            fp = open(tpl, 'r')
            self.html = fp.read()
            fp.close()
        except IOError:
            raise TemplateNotFoundException('Template file not found: %s' %tpl)
            
    def render(self, values={}):
        from string import Template
        t = Template(self.html)
        try:
            from cgi import escape
            for key in values:
                escape(values[key])
            page = t.substitute(values)
        except KeyError:
            log('Template: Template key errors: %s' %str(values))
            self.html = 'Template key errors: %s' %str(values)
            page = 'Template key errors'
        return page


class Controller(object):
    """
    All controllers inherit Controller. Do not forget to set CONTROLLERS_PATH in config.py
"""
    def __init__(self, _request):
        self.request = _request

    @property
    def POST(self):
        return self.request.post

    @property
    def QUERY_STRING(self):
        return self.request.query_string

    def redirect(self, url_append, code=None):
        _code = '303 SEE OTHER' if not code else code
        self.request.header.state(_code)
        self.request.header.add('Location', self.request.base_url + url_append)


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
        '''@usage header.state('404 NOT FOUND')'''
        self.pack[0] = _status

    def add(self, *args):
        '''@usage header.add('Content-Type', 'text/html')'''
        if args:
            self.pack[1].append(args)


class App(object):
    """
    wsgi application wrapper, class is called as a func(tion)
"""
    def __call__(self, environ, start_response):
        from time import time
        start_time = time()

        try:
            booger = [] # debug list
            response_echo = [] # return
            req = Request(environ)
            resp = Response(req)
            booger.append('\n****Request object****\n')
            booger.append(req.debug)

            #check if path is in ROUTES get controller mapped to route
            for route in config.ROUTES:
                url = route[0]
                module, klass = route[1].split('.', 1)
                if url == req.path_info:
                    if self._controller_exists(module + EXT):
                        controller = self._get_controller(module, klass, req)
                        func = getattr(controller, req.method)
                        resp.add([func()])
                        booger.append('\nurl:{0}'.format(url))
                        booger.append('\ncookie_keys:{0}'.format(','.join(req.cookie.keys())) )
                        booger.append('\n\n****Controller object****')
                        booger.append('\nfile.controller.method:{f}.{c}.{m}'.format(f=module, c=klass, m=func.__name__) )                        
                        resp.cookie_header(req.cookie, req.cookie.keys())

                        # break from route loop
                        break

            # not in ROUTES, no break encountered
            else:
                resp.header.state('404 Not Found')
                resp.add([_404()])

            response_echo.append(resp(booger))
        except:
            # @see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi 
            from traceback import format_tb
            e_type, e_value, tb = sys.exc_info() 
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(tb)
            traceback.append('%s: %s' % (e_type.__name__, e_value))
            traceback.append('boogers')
            traceback.extend(booger)
            resp.header.state('500 INTERNAL SERVER ERROR')
            resp.add(booger)
            response_echo.append('<br/>'.join(traceback))
            response_echo.append(''.join(booger))
        finally:
            log('\npykaboo rendered in approximately: %f' %(time()-start_time,))
            start_response(*resp.header.pack[:2])
            return response_echo
                
    def _controller_exists(self, file):
        """
        check if controller file exists in config.CONTROLLER_PATH
    """
        if config.CONTROLLER_PATH:
            controller_file = config.CONTROLLER_PATH + file
        else:
            controller_file = os.path.dirname(__file__) + '/' + file
        return os.path.isfile(controller_file)

    def _get_controller(self, module, klass, req):
        """
        create a controller object 
        @see http://technogeek.org/python-module.html 
        @see http://docs.python.org/library/functions.html#__import__
    """
        sys.path.append(config.CONTROLLER_PATH)
        __import__(module)
        controller_module = sys.modules[module]
        controller_klass = getattr(controller_module, klass)
        controller = controller_klass(req)

        return controller


application = App()

if __name__ == '__main__':
    from wsgiref.validate import validator
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8888, validator(application))
    
    print "Serving on port 8888... (quit) <Ctrl> + C"
    httpd.serve_forever()

