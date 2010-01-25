'''configuration file for pykaboo app'''

import os.path

DEBUG = True
LOG = True

# this works if template folder is same level as config, Ie use absolute path
LOG_PATH = os.path.split(__file__)[0] + '/log/'
TEMPLATES_PATH = os.path.split(__file__)[0] + '/html/'
APP_PATH = os.path.split(__file__)[0] + '/apps/' # '' if in same dir as pyka
DATABASE_DRIVER = 'sqlite'
DATABASE = os.path.split(__file__)[0] + '/data/butiki'

ROUTES = (
    ('/', 'a.Content'),
    ('/content', 'a.Content'),
    ('/test', 'a.Test'),
    ('/foo', 'a.Foo')
)
