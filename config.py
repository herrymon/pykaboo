'''configuration file for pykaboo app'''

import os.path

DEBUG = True
LOG = True

# this works if template folder is same level as config, Ie use absolute path
PYKA_PATH = os.path.realpath(os.path.dirname(__file__))
LOG_PATH = os.path.join(PYKA_PATH, 'log')
TEMPLATES_PATH = os.path.join(PYKA_PATH, 'html')
APP_PATH = os.path.join(PYKA_PATH, 'apps')
DATABASE_DRIVER = 'sqlite'
DATABASE = os.path.join(PYKA_PATH, 'data/butiki')

ROUTES = (
    ('/', 'a.Content'),
    ('/content', 'a.Content'),
    ('/test', 'a.Test'),
    ('/foo', 'a.Foo')
)
