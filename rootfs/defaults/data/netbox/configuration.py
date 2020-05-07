from os import environ as e
from json import loads as parse_json

get = e.get

def get_int(a, b):
    return int(e.get(a, b))

def get_bool(a, b):
    if a in e.keys():
        return e[a].lower() in ['true', '1', 't']
    else:
        return b

#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['netbox.example.com', 'netbox.internal.local']
ALLOWED_HOSTS = e['ALLOWED_HOSTS'].split(',') if 'ALLOWED_HOSTS' in e.keys() else ['*']

# PostgreSQL database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASE = {
    'NAME': get('POSTGRES_DB', 'postgres'),                  # Database name
    'USER': get('POSTGRES_USER', 'postgres'),                 # PostgreSQL username
    'PASSWORD': get('POSTGRES_PASSWORD', 'netbox'),         # PostgreSQL password
    'HOST': get('POSTGRES_HOST', 'postgres'),               # Database server
    'PORT': get('POSTGRES_PORT', '5432'),                   # Database port (leave blank for default)
    'CONN_MAX_AGE': get_int('POSTGRES_CONN_MAX_AGE', 300),  # Max database connection age
}

# Redis database settings. Redis is used for caching and for queuing background tasks such as webhook events. A separate
# configuration exists for each. Full connection details are required in both sections, and it is strongly recommended
# to use two separate database IDs.
REDIS = {
    'tasks': {
        'HOST': get('REDIS_TASKS_HOST', 'redis'),
        'PORT':get_int('REDIS_TASKS_PORT', 6379),
        # Comment out `HOST` and `PORT` lines and uncomment the following if using Redis Sentinel
        # 'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        # 'SENTINEL_SERVICE': 'netbox',
        'PASSWORD': get('REDIS_TASKS_PASSWORD', ''),
        'DATABASE': get_int('REDIS_TASKS_DB', 0),
        'DEFAULT_TIMEOUT': get_int('REDIS_TASKS_DEFAULT_TIMEOUT', 300),
        'SSL': get_bool('REDIS_TASKS_SSL', False),
    },
    'caching': {
        'HOST': get('REDIS_CACHE_HOST', 'redis'),
        'PORT': get_int('REDIS_CACHE_PORT', 6379),
        # Comment out `HOST` and `PORT` lines and uncomment the following if using Redis Sentinel
        # 'SENTINELS': [('mysentinel.redis.example.com', 6379)],
        # 'SENTINEL_SERVICE': 'netbox',
        'PASSWORD': get('REDIS_CACHE_PASSWORD', ''),
        'DATABASE': get_int('REDIS_CACHE_DB', 1),
        'DEFAULT_TIMEOUT': get_int('REDIS_CACHE_DEFAULT_TIMEOUT', 300),
        'SSL': get_bool('REDIS_CACHE_SSL', False),
    }
}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. NetBox will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = get('SECRET_KEY', '')


#########################
#                       #
#   Optional settings   #
#                       #
#########################

# Specify one or more name and email address tuples representing NetBox administrators. These people will be notified of
# application errors (assuming correct email settings are provided).
#ADMINS = [
#    # ['John Doe', 'jdoe@example.com'],
#]
ADMINS = map(lambda s: s.split('::'), e['ADMINS'].split(',')) if 'ADMINS' in e.keys() else []

# Optionally display a persistent banner at the top and/or bottom of every page. HTML is allowed. To display the same
# content in both banners, define BANNER_TOP and set BANNER_BOTTOM = BANNER_TOP.
BANNER_TOP = get('BANNER_TOP', '')
BANNER_BOTTOM = get('BANNER_BOTTOM', '')

# Text to include on the login page above the login form. HTML is allowed.
BANNER_LOGIN = get('BANNER_LOGIN', '')

# Base URL path if accessing NetBox within a directory. For example, if installed at http://example.com/netbox/, set:
# BASE_PATH = 'netbox/'
BASE_PATH = get('BASE_PATH', '')

# Cache timeout in seconds. Set to 0 to dissable caching. Defaults to 900 (15 minutes)
CACHE_TIMEOUT = get_int('CACHE_TIMEOUT', 900)

# Maximum number of days to retain logged changes. Set to 0 to retain changes indefinitely. (Default: 90)
CHANGELOG_RETENTION = get_int('CHANGELOG_RETENTION', 90)

# API Cross-Origin Resource Sharing (CORS) settings. If CORS_ORIGIN_ALLOW_ALL is set to True, all origins will be
# allowed. Otherwise, define a list of allowed origins using either CORS_ORIGIN_WHITELIST or
# CORS_ORIGIN_REGEX_WHITELIST. For more information, see https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = get_bool('CORS_ORIGIN_ALLOW_ALL', False)

#CORS_ORIGIN_WHITELIST = [
#    # 'https://hostname.example.com',
#]
CORS_ORIGIN_WHITELIST = e['CORS_ORIGIN_WHITELIST'].split(',') if 'CORS_ORIGIN_WHITELIST' in e.keys() else []

#CORS_ORIGIN_REGEX_WHITELIST = [
#    # r'^(https?://)?(\w+\.)?example\.com$',
#]
CORS_ORIGIN_REGEX_WHITELIST = map(
  lambda r: compile_regex(r),
  e['CORS_ORIGIN_REGEX_WHITELIST'].split('||')
) if 'CORS_ORIGIN_REGEX_WHITELIST' in e.keys() else []

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
DEBUG = get_bool('DEBUG', False)

# Email settings
EMAIL = {
    'SERVER': get('EMAIL_SERVER', 'localhost'),
    'PORT': get_int('EMAIL_PORT', 25),
    'USERNAME': get('EMAIL_USERNAME', ''),
    'PASSWORD': get('EMAIL_PASSWORD', ''),
    'TIMEOUT': get_int('EMAIL_TIMEOUT', 10),
    'FROM_EMAIL': get('EMAIL_FROM', '')
}

# Enforcement of unique IP space can be toggled on a per-VRF basis. To enforce unique IP space within the global table
# (all prefixes and IP addresses not assigned to a VRF), set ENFORCE_GLOBAL_UNIQUE to True.
ENFORCE_GLOBAL_UNIQUE = get_bool('ENFORCE_GLOBAL_UNIQUE', False)

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
#EXEMPT_VIEW_PERMISSIONS = [
#    # 'dcim.site',
#    # 'dcim.region',
#    # 'ipam.prefix',
#]
EXEMPT_VIEW_PERMISSIONS = e['EXEMPT_VIEW_PERMISSIONS'].split(',') if 'EXEMPT_VIEW_PERMISSIONS' in e.keys() else []

# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = parse_json(e['LOGGING']) if 'LOGGING' in e.keys() else {}

# Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users
# are permitted to access most data in NetBox (excluding secrets) but not make any changes.
LOGIN_REQUIRED = get_bool('LOGIN_REQUIRED', False)

# The length of time (in seconds) for which a user will remain logged into the web UI before being prompted to
# re-authenticate. (Default: 1209600 [14 days])
#LOGIN_TIMEOUT = None
LOGIN_TIMEOUT = get_int('LOGIN_TIMEOUT', 1209600)

# Setting this to True will display a "maintenance mode" banner at the top of every page.
MAINTENANCE_MODE = get_bool('MAINTENANCE_MODE', False)

# An API consumer can request an arbitrary number of objects =by appending the "limit" parameter to the URL (e.g.
# "?limit=1000"). This setting defines the maximum limit. Setting it to 0 or None will allow an API consumer to request
# all objects by specifying "?limit=0".
MAX_PAGE_SIZE = get_int('MAX_PAGE_SIZE', 1000)

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed. Note that
# the default value of this setting is derived from the installed location.
# MEDIA_ROOT = '/opt/netbox/netbox/media'
MEDIA_ROOT = get('MEDIA_ROOT', '/data/netbox/media')

# By default uploaded media is stored on the local filesystem. Using Django-storages is also supported. Provide the
# class path of the storage driver in STORAGE_BACKEND and any configuration options in STORAGE_CONFIG. For example:
# STORAGE_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'
# STORAGE_CONFIG = {
#     'AWS_ACCESS_KEY_ID': 'Key ID',
#     'AWS_SECRET_ACCESS_KEY': 'Secret',
#     'AWS_STORAGE_BUCKET_NAME': 'netbox',
#     'AWS_S3_REGION_NAME': 'eu-west-1',
# }
if 'STORAGE_CONFIG' in e.keys():
    STORAGE_CONFIG = parse_json(e['STORAGE_CONFIG'])

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
METRICS_ENABLD = get_bool('METRICS_ENABLED', False)

# Credentials that NetBox will uses to authenticate to devices when connecting via NAPALM.
NAPALM_USERNAME = get('NAPALM_USERNAME', '')
NAPALM_PASSWORD = get('NAPALM_PASSWORD', '')

# NAPALM timeout (in seconds). (Default: 30)
NAPALM_TIMEOUT = get_int('NAPALM_TIMEOUT', 30)

# NAPALM optional arguments (see http://napalm.readthedocs.io/en/latest/support/#optional-arguments). Arguments must
# be provided as a dictionary.
NAPALM_ARGS = parse_json(e['NAPALM_ARGS']) if 'NAPALM_ARGS' in e.keys() else {}

# Determine how many objects to display per page within a list. (Default: 50)
PAGINATE_COUNT = get_int('PAGINATE_COUNT', 50)

# Enable installed plugins. Add the name of each plugin to the list.
PLUGINS = e['PLUGINS'].split(',') if 'PLUGINS' in e.keys() else []

# Configure enabled plugins. This should be a dictionary of dictionaries, mapping each plugin by name to its configuration parameters.
PLUGINS_CONFIG = parse_json(e['PLUGINS_CONFIG']) if 'PLUGINS_CONFIG' in e.keys() else {}

# When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to
# prefer IPv4 instead.
PREFER_IPV4 = get_bool('PREFER_IPV4', False)

# Remote authentication support
REMOTE_AUTH_ENABLED = get_bool('REMOTE_AUTH_ENABLED', False)
REMOTE_AUTH_BACKEND = get('REMOTE_AUTH_BACKEND', 'utilities.auth_backends.RemoteUserBackend')
REMOTE_AUTH_HEADER = get('REMOTE_AUTH_HEADER', 'HTTP_REMOTE_USER')
REMOTE_AUTH_AUTO_CREATE_USER = get_bool('REMOTE_AUTH_AUTO_CREATE_USER', True)
REMOTE_AUTH_DEFAULT_GROUPS = e['REMOTE_AUTH_DEFAULT_GROUPS'].split(',') if 'REMOTE_AUTH_DEFAULT_GROUPS' in e.keys() else []
REMOTE_AUTH_DEFAULT_PERMISSIONS = e['REMOTE_AUTH_DEFAULT_PERMISSIONS'].split(',') if 'REMOTE_AUTH_DEFAULT_PERMISSIONS' in e.keys() else []

# This determines how often the GitHub API is called to check the latest release of NetBox. Must be at least 1 hour.
RELEASE_CHECK_TIMEOUT = get_int('RELEASE_CHECK_TIMEOUT', (24 * 3600))

# This repository is used to check whether there is a new release of NetBox available. Set to None to disable the
# version check or use the URL below to check for release in the official NetBox repository.
#RELEASE_CHECK_URL = None
# RELEASE_CHECK_URL = 'https://api.github.com/repos/netbox-community/netbox/releases'
RELEASE_CHECK_URL = get('RELEASE_CHECK_URL', None)

# The file path where custom reports will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
# REPORTS_ROOT = '/opt/netbox/netbox/reports'
REPORTS_ROOT = get('REPORTS_ROOT', '/data/netbox/reports')

# The file path where custom scripts will be stored. A trailing slash is not needed. Note that the default value of
# this setting is derived from the installed location.
# SCRIPTS_ROOT = '/opt/netbox/netbox/scripts'
SCRIPTS_ROOT = get('SCRIPTS_ROOT', '/data/netbox/scripts')

# Enable plugin support in netbox. This setting must be enabled for any installed plugins to function.
#PLUGINS_ENABLED = False
PLUGINS_ENABLED = get_bool('PLUGINS_ENABLED', False)

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
# PLUGINS_CONFIG = {
#     'my_plugin': {
#         'foo': 'bar',
#         'buzz': 'bazz'
#     }
# }
if 'PLUGINS_CONFIG' in e.keys():
    PLUGINS_CONFIG = parse_json(e['PLUGINS_CONFIG'])

# By default, NetBox will store session data in the database. Alternatively, a file path can be specified here to use
# local file storage instead. (This can be useful for enabling authentication on a standby instance with read-only
# database access.) Note that the user as which NetBox runs must have read and write permissions to this path.
SESSION_FILE_PATH = get('SESSION_FILE_PATH', None)

# Time zone (default: UTC)
if 'TIME_ZONE' in e.keys():
    TIME_ZONE = e['TIME_ZONE']
elif 'TZ' in e.keys():
    TIME_ZONE = e['TZ']
else:
    TIME_ZONE = 'UTC'

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date
DATE_FORMAT = get('DATE_FORMAT', 'N j, Y')
SHORT_DATE_FORMAT = get('SHORT_DATE_FORMAT', 'Y-m-d')
TIME_FORMAT = get('TIME_FORMAT', 'g:i a')
SHORT_TIME_FORMAT = get('SHORT_TIME_FORMAT', 'H:i:s')
DATETIME_FORMAT = get('DATETIME_FORMAT', 'N j, Y g:i a')
SHORT_DATETIME_FORMAT = get('SHORT_DATETIME_FORMAT', 'Y-m-d H:i')
