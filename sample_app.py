# sample pykaboo app
import os.path
from pyka import application, serve, post, get, bind
from pyka import mako_render
from pyka import PYKA_PATH

template_path = os.path.join(PYKA_PATH, 'html')

@get('/')
def index():
    return 'index of app' + index.request.base_url

@get('/greet/[a-z]*')
def greet():
    return 'hello, ' + greet.request.path[1]

@get('/mako')
def templated():
    return mako_render('mako_sample.html', template_paths=[template_path], body="test")

@get('/sayform')
def sayform():
    return """
    <form method="post" action="/say">
    <input type=text name="message"/>
    <input type=text name="message"/>
    <input type=submit value="go"/>
    </form>"""

@post('/say')
def say():
    msg = say.request.post.getvalue('message')
    return msg

if __name__ == '__main__':
    serve(application)
