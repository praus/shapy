import socket
from shapy.framework.exceptions import ImproperlyConfigured

def validate_ip(addr):
    assert isinstance(addr, str), "IP address must be a string"
    try:
        socket.inet_aton(addr)
    except socket.error:
        raise ImproperlyConfigured("Invalid IP: %s" % addr)


def align(l, alignto=4):
    """Aligned length to nearest multiple of 4."""
    return (l + alignto - 1) & ~(alignto - 1)


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
