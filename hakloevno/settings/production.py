from .base import *

DEBUG = False

# Try to import local overrides
try:
    from .local import *
except ImportError:
    pass
