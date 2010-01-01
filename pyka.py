'''an attempt at a DIY wsgi framework, 
inspired by:
Ian Bicking tutorial @see http://pythonpaste.org/webob/do-it-yourself.html
web.py 
bottle.py

MVC? sort of... ''' 

__version__ = '0.1'
__author__ = 'Erick B email:herrymonster@gmail.com'
__license__ = 'use at your own risk'

import os, sys
sys.path.append(os.path.dirname(__file__))   #@see http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
import config
from Cookie import SimpleCookie

'''errors and logger'''
class HTTPRequestException(Exception): pass

if config.DEBUG:
    def log(msg):
        from datetime import datetime
        dbg_file = config.LOG_PATH + 'debug_%d_%d_%d.txt'%(datetime.now().year,datetime.now().month, datetime.now().day)
        fp = open(dbg_file, 'a+')
        fp.write(msg + '\n')
        fp.close()
else:
    def log(msg): pass


#utility functions

def dictify(input_text):
    '''convert wsgi.input to {}
Eg name=Erick&time=11pm to {'name':['Erick'], 'time':['11pm']}
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
    '''no route found put a Template here'''
    return 'Page not found'

class Template(object):
    '''wrapper for string.Template 
@see http://docs.python.org/library/string.html#template-strings'''
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
            page = t.substitute(values)
        except KeyError:
            log('Template: Template key errors: %s' %str(values))
            self.html = 'Template key errors: %s' %str(values)
            page = 'Template key errors'
        return page


class Controller(object):
    '''controller base'''
    def __init__(self, **kwargs):
        self.path = kwargs.get('p',[])
        self.input = kwargs.get('i',{})


class Header(object):
    '''response header and status object, arg to start_response'''
    def __init__(self, status='200 OK', headers=[]):
        self.status = status
        self.headers = headers
        log('Header: Created header[status=%s, header=[%s]]' %(status, ','.join(headers)) )

    def state(self, status):
        self.status = status

    def add(self, *args):
        if args:
            self.headers.append(args)
    

class App(object):
    '''wsgi application wrapper'''
    def __call__(self, environ, start_response):
        from time import time
        start_time = time()
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO'].split('/')
        head.add('Content-Type', 'text/html')

        #check if path is in ROUTES get controller mapped to route
        for route in config.ROUTES:
            url, module = route
            if url == environ['PATH_INFO']:
                if self._controller_exists(module + config.EXT):
                    if method.upper() == 'POST':
                        input = dictify(environ['wsgi.input'].read())
                    elif method.upper() == 'GET':
                        input = dictify(environ.get('QUERY_STRING', 'query_string'))
                    else:
                        raise HTTPRequestException

                    controller = self._get_controller(module, path, input)
                    func = getattr(controller, method.lower())
                    head.state('200 OK')
                    response = func()
                    if environ.has_key('HTTP_COOKIE') and environ['HTTP_COOKIE']:
                        c = SimpleCookie(environ['HTTP_COOKIE'])
                        tmp = int(c['test'].value)
                        c['test'] = str(tmp + 1)
                    else:
                        c = SimpleCookie()
                        c['test'] = 0
                    response += c['test'].value
                    head.add('Set-Cookie', 'test='+c['test'].value)
                    break

        # not in ROUTES
        else:
            log('''
                path info:%s 
                config.CONTROLLER_PATH:%s
                routes: %s'''
                %(environ['PATH_INFO'], config.CONTROLLER_PATH, str(config.ROUTES))
            )
            head.state('404 Not Found')
            response = _404()

        start_response(head.status, head.headers)
        log('pykaboo rendered in approximately: %f' %(time()-start_time,))
        return response
            
    def _controller_exists(self, file):
        '''check if controller file exists in config.CONTROLLER_PATH'''
        if config.CONTROLLER_PATH:
            controller_file = config.CONTROLLER_PATH + file
        else:
            controller_file = os.path.dirname(__file__) + '/' + file
        return os.path.isfile(controller_file)

    def _get_controller(self, candidate, path=[], input={}):
        '''create a controller object
@see http://technogeek.org/python-module.html 
@see http://docs.python.org/library/functions.html#__import__'''
        if config.CONTROLLER_PATH:
            sys.path.append(config.CONTROLLER_PATH)
        __import__(candidate)
        module = sys.modules[candidate]
        controller_klass = getattr(module, candidate)
        #controller = controller_klass({'p':path, 'i':input}) # can't use? p=path and i=input
        controller = controller_klass(p=path, i=input) # can't use? p=path and i=input
        return controller


app = App()
head = Header()
application = app
