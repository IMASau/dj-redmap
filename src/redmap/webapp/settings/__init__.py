"""
Magically import `webapp.settings.development` when `webapp.settings` is
imported
"""

from redmap.webapp.settings.base import *

try:
    from redmap.webapp.settings.local import *
except ImportError:
    pass
