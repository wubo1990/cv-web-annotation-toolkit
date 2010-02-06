# Django settings for annotation project.

import os

DEBUG = True
if "DJANGO_IN_APACHE" in os.environ:
	DEBUG = False
	pass


TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Alexander Sorokin', 'sorokin2@uiuc.edu'),
)

MANAGERS = ADMINS


DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'annotations_v2'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.	
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
SITE_NAME = 'vision-app1.cs.uiuc.edu'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

DEFAULT_CHARSET = 'utf-8'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Required for RPC4Django authenticated method calls
    # Requires Django 1.1+
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'snippets.basic_auth.BasicAuthenticationMiddleware',

    'django.middleware.doc.XViewMiddleware',
)

# Required for RPC4Django authenticated method calls
# Requires Django 1.1+
AUTHENTICATION_BACKENDS = (
       'django.contrib.auth.backends.ModelBackend',
       'django.contrib.auth.backends.RemoteUserBackend',
)

BASIC_WWW_AUTHENTICATION=True

ROOT_URLCONF = 'crowd_server.urls'

DATASETS_ROOT = '/var/datasets/'
SEGMENTATION_ROOT = DATASETS_ROOT+'segmentations/'

DJ_CODE_RT='/var/django/web_annotations_server/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
    DJ_CODE_RT+"templates/",
    #"/var/lib/python-support/python2.5/django/contrib/admin/templates/",
)


DEFAULT_FROM_EMAIL='syrnick@gmail.com'
EMAIL_HOST='localhost'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'tagging',
    'registration',
    'rpc4django',

    'crowd_server.mturk',
    'crowd_server.datastore',

)


#Registration app settings
ACCOUNT_ACTIVATION_DAYS=4


#Mturk app settings
HOST_NAME_FOR_MTURK="http://vision-app1.cs.uiuc.edu/"

MTURK_BLOCK_WORKER_MIN_UTILITY=30

MTURK_QUALIFICATIONS_PREFIX="CD DJ: "

## number of hits to show per page
NUM_HITS_PER_PAGE = 20


