#!/usr/bin/python

import logging
logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
                    format='%(asctime)s %(levelname)s: %(message)s')

from shapy import register_settings
register_settings('settings')
from shapy.emulation.shaper import Shaper

notice = """\
This will clear entire Traffic Control configuration and unload IFB module.
Please note reported errors usually do not mean anything bad, just that there
was nothing to tear down on that particular interface."""

if __name__ == '__main__':
    from shapy import settings
    print "Tearing down all interfaces: %s" % ', '.join(settings.EMU_INTERFACES)
    print notice
    print "-"*80
    sh = Shaper()
    sh.teardown_all()
