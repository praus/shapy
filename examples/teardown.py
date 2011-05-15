#!/usr/bin/python

import logging
logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
                    format='%(asctime)s %(levelname)s: %(message)s')

def scan_interfaces():
    """Parses a list of all interfaces reported by `ip link`"""
    import subprocess
    import re
    ifcs = []
    out = subprocess.check_output(["ip", "link"]).split('\n')
    for line in out:
        m = re.match("^[0-9]+:[ ]([a-z0-9]+):", line)
        if m:
            ifcs.append(m.group(1))
    return ifcs


from shapy import register_settings
register_settings('settings')
from shapy.emulation.shaper import Shaper

from shapy import settings
settings.EMU_INTERFACES = scan_interfaces()

notice = """\
This will clear entire Traffic Control configuration and unload IFB module.
Please note reported errors usually do not mean anything bad, just that there
was nothing to tear down on that particular interface."""

if __name__ == '__main__':
    print "Tearing down all interfaces: %s" % ', '.join(settings.EMU_INTERFACES)
    print notice
    print "-"*80
    sh = Shaper()
    sh.teardown_all()
