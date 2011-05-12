import socket
import re
from shapy.framework.exceptions import ImproperlyConfigured
from shapy.framework.executor import run

def validate_ip(addr):
    assert isinstance(addr, str), "IP address must be a string"
    try:
        socket.inet_aton(addr)
    except socket.error:
        raise ImproperlyConfigured("Invalid IP: %s" % addr)

def align(l, alignto=4):
    """Aligned length to nearest multiple of 4."""
    return (l + alignto - 1) & ~(alignto - 1)

def convert_handle(str_handle):
    """
    Takes string handle such as 1: or 10:1 and creates a binary number accepted
    by the kernel Traffic Control.
    """
    major, minor = str_handle.split(':')    # "major:minor"
    minor = minor if minor else '0'
    return int(major, 16) << 16 | int(minor, 16)

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
