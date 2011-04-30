import socket
from shapy.exceptions import ImproperlyConfigured

def validate_ip(addr):
    assert isinstance(addr, str), "IP address must be a string"
    try:
        socket.inet_aton(addr)
    except socket.error:
        raise ImproperlyConfigured("Invalid IP: %s" % addr)