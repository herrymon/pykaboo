# sample pykaboo app
import os.path
from pyka import application, bind, serve
from pyka import mako_render
from pyka import PYKA_PATH

template_path = os.path.join(PYKA_PATH, 'html')

@bind('/')
def index():
    return 'index of app' + index.request.base_url

@bind('/hello')
def hello():
    return 'hello' + hello.request.path[0]

@bind('/greet/[a-z]*')
def greet():
    return 'hello, ' + greet.request.path[1]

@bind('/mako')
def templated():
    return mako_render('mako_sample.html', template_paths=[template_path], body="test")

serve(application)
