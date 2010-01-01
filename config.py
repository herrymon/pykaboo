'''configuration file for pykaboo app'''

import os.path

DEBUG = True

EXT = '.py'

# this works if template folder is same level as config, Ie use absolute path
LOG_PATH = os.path.split(__file__)[0] + '/log/'
TEMPLATES_PATH = os.path.split(__file__)[0] + '/html/'
CONTROLLER_PATH = os.path.split(__file__)[0] + '/controllers/' # '' if in same dir as pyka

ROUTES = (
    ('/', 'Content'),
    ('/content', 'Content'),
)
