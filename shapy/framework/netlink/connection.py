import os
import socket
import struct
from .constants import *
from .message import Message

class Connection(object):
    """
    Object representing Netlink socket connection to the kernel.
    """
    def __init__(self, nlservice=socket.NETLINK_ROUTE, groups=0):
        # nlservice = Netlink IP service
        self.fd = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, nlservice)
        self.fd.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        self.fd.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.fd.bind((0, groups)) # pid=0 lets kernel assign socket PID
        self.pid, self.groups = self.fd.getsockname()
        self._seq = 0
    
    def send(self, msg):
        if isinstance(msg, Message):
            if msg.seq == -1: 
                msg.seq = self.seq()
            msg.pid = self.pid
            msg = msg.pack()
        self.fd.send(msg)
    
    def recv(self):
        contents, (nlpid, nlgrps) = self.fd.recvfrom(16384)
        msg = Message.unpack(contents)
        
        if msg.type == NLMSG_ERROR:
            errno = -msg.service_template.error_code
            #errno = -struct.unpack("i", msg.payload[:4])[0]
            if errno != 0:
                err = OSError("Netlink error: %s (%d) | msg: %s" % (
                    os.strerror(errno), errno, msg.service_template.old_message))
                err.errno = errno
                raise err
        return msg
    
    def seq(self):
        self._seq += 1
        return self._seq