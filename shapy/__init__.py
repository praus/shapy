VERSION = "1.0"

import sys
import shapy
import shapy.framework.settings.default
setattr(shapy, 'settings', sys.modules['shapy.framework.settings.default'])

def register_settings(module_name):
    __import__(module_name)
    custom = sys.modules[module_name]
    for name in ( m for m in custom.__dict__ if not m.startswith('__') ):
        setattr(shapy.settings, name, getattr(custom, name))
