# For web application:
APP_PORT = 8000
APP_HOST = 'localhost'

# For csrf protection:
FORM_FIELD_NAME = 'csrf_token'
COOKIE_NAME = '_csrf_token'
SECRET_PHRASE = 'hui123'

# For redis:
REDIS_DB_INDEX = 5
REDIS_PWD = '?password=HEXagonDELTA'
REDIS_ADDR = F'redis://localhost/{REDIS_DB_INDEX}'
REDIS_ADDR_PROTECTED = REDIS_ADDR + REDIS_PWD

# For jinja templates:
TMPL_FOLDER = 'templates'
STATIC_ROOT_URL = '/static'

# For MySQL Database:
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PWD = '1234'
DB_NAME = 'webchat'
