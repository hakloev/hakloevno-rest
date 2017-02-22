from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0!%_3&_f6(#ajeesqkti9@ydju*lfa0%zau1i0kkvv6b23&j1&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = ['*']

# Try to import local overrides
try:
    from .local import *
except ImportError:
    pass
