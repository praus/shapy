import unittest2
import imp
import sys
import shapy

class TestSettings(unittest2.TestCase):

    def setUp(self):
        self.settings = imp.new_module('test_settings')
        sys.modules.update(test_settings=self.settings)
        setattr(self.settings, 'UNITS', 'override')
        setattr(self.settings, 'NEW_OPTION', 'new')

    def test_settings_override(self):
        shapy.register_settings('test_settings')
        from shapy import settings
        self.assertEqual(settings.UNITS, 'override')
        self.assertEqual(getattr(settings, 'NEW_OPTION', None), 'new')