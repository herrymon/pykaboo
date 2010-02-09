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

# <regex_path>__<script>__<App class>
ROUTES = (
    r"/__a__Content",
    r"/foo/[a-z]__a__Foo",
    r"/content__a__Content",
    r"/test__a__Test",
    r"/mia__mia__Mia",
    r"/mako__a__MakoTest"
)
