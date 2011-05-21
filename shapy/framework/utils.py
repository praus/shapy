import socket
import re
import struct
from shapy.framework.exceptions import ImproperlyConfigured
from shapy.framework.executor import run
from shapy import settings

with open('/proc/net/psched', 'rb') as f:
    psched = f.read()
ns_per_usec, ns_per_tick = psched.strip().split()[:2]
ns_per_usec = struct.unpack(">I", ns_per_usec.decode('hex'))[0]
ns_per_tick = struct.unpack(">I", ns_per_tick.decode('hex'))[0]
ticks_per_usec = float(ns_per_usec) / float(ns_per_tick)

def validate_ip(addr):
    assert isinstance(addr, str), "IP address must be a string"
    try:
        socket.inet_aton(addr)
    except socket.error:
        raise ImproperlyConfigured("Invalid IP: %s" % addr)

def align(l, alignto=4):
    """Aligned length to nearest multiple of 4."""
    return (l + alignto - 1) & ~(alignto - 1)

def convert_handle(handle):
    """
    Takes string handle such as 1: or 10:1 and creates a binary number accepted
    by the kernel Traffic Control.
    """
    if isinstance(handle, str):
        major, minor = handle.split(':')    # "major:minor"
        minor = minor if minor else '0'
        return int(major, 16) << 16 | int(minor, 16)
    return handle

def get_if_index(if_name):
    """
    Retrieves interface index based on interface name.
    Ugly implementation of if_nametoindex() from net/if.h
    """
    out = run("ip link show dev {interface}".format(interface=if_name))
    try:
        return int(re.match('^([0-9]+)', out).group(0), 10)
    except:
        return 0

def nl_us2ticks(delay):
    """Convert microseconds to timer ticks."""
    return int(ticks_per_usec * delay)

def nl_ticks2us(ticks):
    """Convert ticks to microseconds."""
    return ticks / ticks_per_usec

def convert_to_bytes(rate):
    """
    Converts rate in kilobits or kilobytes to bytes based on shapy.settings
    """
    r = rate * 1000
    if settings.UNITS == "kbit":
        r = r / 8
    return r

class InterpreterMixin(object):
    interpreters = {}
    
    @classmethod
    def register(cls, interpreter, content_types):
        for type in content_types:
            cls.interpreters.update({type: interpreter})
    
    @classmethod
    def select(cls, selector):
        """Selects interpreter object based on the selector."""
        return cls.interpreters[selector]
