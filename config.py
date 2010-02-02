'''configuration file for pykaboo app'''

import os.path

DEBUG = True
LOG = True

# ok to use absolute paths (this is more flexible Eg transferring servers) 
PYKA_PATH = os.path.realpath(os.path.dirname(__file__))
LOG_PATH = os.path.join(PYKA_PATH, 'log')
TEMPLATES_PATH = os.path.join(PYKA_PATH, 'html')
APP_PATH = os.path.join(PYKA_PATH, 'apps')
DATABASE_DRIVER = 'sqlite3'
DATABASE_PATH = os.path.join(PYKA_PATH, 'data')
DATABASE_FILE = os.path.join(DATABASE_PATH, 'butiki')

# <path>__<script>__<App class>
ROUTES = (
    "/__a__Content",
    "/content__a__Content",
    "/test__a__Test",
    "/foo__a__Foo",
    "/mia__mia__Mia"
)
