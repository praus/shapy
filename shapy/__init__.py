import sys
import shapy
import shapy.settings.default
setattr(shapy, 'settings', sys.modules['shapy.settings.default'])

def register_settings(module_name):
    __import__(module_name)
    setattr(shapy, 'settings', sys.modules[module_name])
