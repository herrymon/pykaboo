# sample pykaboo app

from pyka import application, bind, serve

@bind('/')
def index():
    return 'index of app'

@bind('/')
def duplicate_index():
    return 'duplicate_index of app'

@bind('/hello')
def hello():
    return 'hello'

@bind('/greet/[a-z]+')
def greet():
    return 'hello, ' + path[1]


serve(application)
