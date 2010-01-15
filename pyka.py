'''an attempt at a tiny wsgi framework, 
inspired by: Ian Bicking tutorial @see http://pythonpaste.org/webob/do-it-yourself.html, 

Code concepts, ideas borrowed from:
web.py @see http://webpy.org/
bottle.py @see http://github.com/defnull/bottle.
werkzeug @see http://werkzeug.pocoo.org/
django @see http://www.djangoproject.com
''' 

__version__ = '0.1'
__author__ = 'Erick :-) email: herrymonster@gmail.com'
__license__ = 'do whatever you want Ie use at your own risk'

import os, sys
sys.path.append(os.path.dirname(__file__))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
import config
from Cookie import SimpleCookie
from datetime import datetime

'''errors and logger'''
class HTTPRequestException(Exception): pass

if config.DEBUG:
    def log(msg):
        import logging
        now = datetime.now()
        log_file = '%s%d_%d_%d.log' %(config.LOG_PATH, now.year, now.month, now.day)
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        logging.debug(msg)
else:
    def log(msg): 
        msg = None


#utility functions
def dictify(input_text):
    '''convert wsgi.input to {}
Eg name=Erick&time=11pm to {'name': ['Erick'], 'time': ['11pm']}
'''
    log('xutils.dictify: %d %s' %(len(input_text), input_text))
    dict = {}
    if input_text:
        post = input_text.split('&')
        for val in post:
            key, value = val.split('=')
            #what if we need the space later? edge case?
            #tried this without strip() space is replaced by '+', I have to google that
            value = value.strip()

            if dict.has_key(key):
                if not isinstance(dict[key], list):
                    dict[key] = [dict[key]]
                dict[key].append(value) #keep adding for array type inputs 
            else:
                dict[key] = value
    return dict

def _404():
    '''no route found, put a Template here'''
    return 'Page not found'

#main components
class Response(object):
    '''use this for start_response'''
    def __init__(self, _request):
        self.response = []
        self.request = _request
        self.header = Header()

    def add(self, resp=None):
        self.response.extend(resp)

    def __call__(self):
        if self.request.method == 'HEAD':
            return ''
        else:
            return ''.join(self.response)


class Request(object):
    '''container of WSGI environ object'''
    def __init__(self, _env):
        self.method = _env.get('REQUEST_METHOD', None).lower()
        self.post = self._post(_env.get('wsgi.input', None))
        self.query_string = dictify(_env.get('QUERY_STRING',''))
        self.cookie = SimpleCookie(_env.get('HTTP_COOKIE',''))
        self.path_info = _env.get('PATH_INFO','')
        self.path = self.path_info.split('/')
        self._cookie()

    def __str__(self):
        return '''method: %s
post: %s
query_string: %s
cookie: %s
path_info: %s
path: %s''' %(self.method, str(self.post), str(self.query_string), str(self.cookie), self.path_info, str(self.path)) 

    def _method(self):
        if not self.method.upper() in ('GET', 'POST'):
            raise HTTPRequestException('HTTP method is not supported only GET and POST is supported')

    def _post(self, _env_post):
        _dict_post = {}
        if _env_post:
            _dict_post = dictify(_env_post.read())
        else:
            _dict_post = {}
        return _dict_post

    def _cookie(self):
        # add an incrementing cookie, testing usge of Cookie module, have to improve this later
        try:
            self.cookie['pyka'] = int(self.cookie['pyka'].value) + 1
        except KeyError:
            self.cookie['pyka'] = 0
        

class Template(object):
    '''instantiate with filename of html template file. Do not forget to set TEMPLATE_PATH in config.py. 
wrapper for string.Template @see http://docs.python.org/library/string.html#template-strings'''
    def __init__(self, tfile, echo=True):
        try:
            self.echo = echo
            tpl = config.TEMPLATES_PATH + tfile
            fp = open(tpl, 'r')
            self.html = fp.read()
            fp.close()
        except IOError:
            log('Template: Template file not found/read: %s' %tpl)
            self.html = 'Template: Template not found %s' %tpl
            
    def render(self, values={}):
        from string import Template
        t = Template(self.html)
        try:
            from cgi import escape
            for key in values:
                escape(values[key],'&<>')
            page = t.substitute(values)
        except KeyError:
            log('Template: Template key errors: %s' %str(values))
            self.html = 'Template key errors: %s' %str(values)
            page = 'Template key errors'
        return page


class Controller(object):
    '''all your controllers inherit this. Do not forget to set CONTROLLERS_PATH in config.py'''
    def __init__(self, *args):
        self.PATH, self.POST, self.QUERY_STRING, self.COOKIES = args


class Header(object):
    '''status object and response headers packed to use as arg to start_response()'''
    def __init__(self, _status=None, _headers=None):
        '''@usage start_response(*header.pack)'''
        self.pack = []
        if _status:
            self.pack.append(_status)
        else:
            self.pack.append('200 OK')
        if _headers:
            self.pack.append(_headers)
        else:
            self.pack.append([])
        log('Header: Created header[status=%s, header=[%s]]' %(self.pack[0], ','.join(self.pack[1])) )

    def state(self, _status):
        '''@usage header.state('404 NOT FOUND')'''
        self.pack[0] = _status

    def add(self, *args):
        '''@usage header.add('Content-Type', 'text/html')'''
        if args:
            self.pack[1].append(args)


class App(object):
    '''wsgi application wrapper, class is called as a func(tion)'''
    def __call__(self, environ, start_response):
        from time import time
        start_time = time()

        try:
            #check if path is in ROUTES get controller mapped to route
            req = Request(environ)
            resp = Response(req)
            response_echo = ''
            booger = []
            booger.append('<pre>')
            booger.append(str(req))
            for route in config.ROUTES:
                url = route[0]
                module, klass = route[1].split('.', 1)
                booger.append('\nurl:%s\ncontroller script:%s\nklass:%s'%(url, module, klass))
                if url == req.path_info:
                    if self._controller_exists(module + config.EXT):
                        # only supporting POST GET HEAD for now, have to read up about PUT DELETE HEAD OPTIONS and other methods
                        controller = self._get_controller(module, klass, req.path, req.post, req.query_string, {})
                        func = getattr(controller, req.method)
                        booger.append('\nstr(func)' + str(func))                        
                        resp.header.add('Content-Type', 'text/html')
                        resp.header.state('200 OK')
                        resp.header.add('Set-Cookie', 'pyka='+req.cookie['pyka'].value)
                        resp.add([func()])
                        resp.add(req.cookie['pyka'].value)
                        break

            # not in ROUTES
            else:
                resp.header.add('Content-Type', 'text/plain')
                resp.header.state('404 Not Found')
                resp.add([_404()])

            #start_response(*header.pack)
            response_echo = resp() + ''.join(booger)
        except:
            # @see http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi 
            from sys import exc_info
            from traceback import format_tb
            e_type, e_value, tb = exc_info() 
            traceback = ['Traceback (most recent call last):']
            traceback += format_tb(tb)
            traceback.append('%s: %s' % (e_type.__name__, e_value))
            traceback.append('boogers')
            traceback.extend(booger)
            resp.header.state('500 INTERNAL SERVER ERROR')
            if config.DEBUG:
                booger.append('</pre>')
                resp.add(booger)
            response_echo = '<br/>'.join(traceback) + ''.join(booger)
        finally:
            log('pykaboo rendered in approximately: %f' %(time()-start_time,))
            start_response(*resp.header.pack)
            yield response_echo
                
    def _controller_exists(self, file):
        '''check if controller file exists in config.CONTROLLER_PATH'''
        if config.CONTROLLER_PATH:
            controller_file = config.CONTROLLER_PATH + file
        else:
            controller_file = os.path.dirname(__file__) + '/' + file
        return os.path.isfile(controller_file)

    def _get_controller(self, module, klass, path=None, post=None, get=None, cookies=None):
        '''create a controller object @see http://technogeek.org/python-module.html 
@see http://docs.python.org/library/functions.html#__import__'''
        sys.path.append(config.CONTROLLER_PATH)
        __import__(module)
        controller_module = sys.modules[module]
        controller_klass = getattr(controller_module, klass)
        controller = controller_klass(path, post, get, cookies)

        return controller


app = App()
application = app
