"""
This module contains code pertaining to the generic messaging on a Netlink socket.
"""

#There are three levels to a Netlink message: The general Netlink
#message header, the IP service specific template, and the IP service
#specific data.
    
# 0                   1                   2                   3
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|                                                               |
#|                   Netlink message header                      |
#|                                                               |
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|                                                               |
#|                  IP Service Template                          |
#|                                                               |
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|                                                               |
#|                  IP Service specific data in TLVs             |
#|                                                               |
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

import quopri, binascii
import struct
from struct import Struct
from shapy.framework.utils import align, InterpreterMixin
from .constants import *

class Message(object):
    """Object representing the entire Netlink message."""
    #0                   1                   2                   3
    #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                          Length                             |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|            Type              |           Flags              |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                      Sequence Number                        |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                      Process ID (PID)                       |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    
    #struct nlmsghdr {
    #   __u32 nlmsg_len;    /* Length of message including header. */
    #   __u16 nlmsg_type;   /* Type of message content. */
    #   __u16 nlmsg_flags;  /* Additional flags. */
    #   __u32 nlmsg_seq;    /* Sequence number. */
    #   __u32 nlmsg_pid;    /* PID of the sending process. */
    #};
    
    nlmsghdr = Struct("IHHII")
    
    @classmethod
    def unpack(cls, msg):
        """Unpack raw bytes into a Netlink message."""
        mlength, type, flags, seq, pid = cls.nlmsghdr.unpack(msg[:cls.nlmsghdr.size])
        st_cls = ServiceTemplate.select(type)
        st = st_cls.unpack(msg[cls.nlmsghdr.size:])
        return Message(type, flags, seq, service_template=st)
    
    def __init__(self, type, flags=0, seq=-1, service_template=None):
        """Used for creating Netlink messages."""
        self.type = type
        self.flags = flags
        self.seq = seq
        self.pid = 0
        self.service_template = service_template
        self.service_template.message = self

    def __len__(self):
        """Aligned length of service template message + attributes."""
        return align(self.nlmsghdr.size + len(self.payload))
    
    def pack_header(self):
        return self.nlmsghdr.pack(len(self), self.type, self.flags, self.seq, self.pid)

    def pack(self):
        return self.pack_header() + self.payload

    @property
    def payload(self):
        return self.service_template.pack()
    
    def __repr__(self):
        return '<netlink message type=%s, pid=%s, seq=%s, flags=0x%x>' % (
            self.type, self.pid, self.seq, self.flags)


class ServiceTemplate(InterpreterMixin):
    """Represents the second part of the Netlink message."""
    @classmethod
    def unpack(cls, data):
        rest = data[cls.format.size:]
        st_instance = cls(*cls.format.unpack(data[:cls.format.size]))
        st_instance.attributes = tuple(st_instance.unpack_attrs(rest))
        return st_instance
    
    def pack(self):
        return ''
    
    def pack_attrs(self):
        return ''.join(( a.pack() for a in self.attributes ))
    
    def unpack_attrs(self, data):
        while True:
            attr, data = Attr.unpack(data)
            attr.service_template = self
            yield attr
            if not data: break


class ACK(ServiceTemplate):
    """
    Netlink ACK message representation (RFC 3549, p. 12).
    """
    # 0                   1                   2                   3
    # 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                       Netlink message header                  |
    #|                       type = NLMSG_ERROR                      |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                          Error code                           |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                       OLD Netlink message header              |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    
    format = Struct('i')
    
    @classmethod
    def unpack(cls, data):
        rest = data[cls.format.size:]
        st_instance = cls(*cls.format.unpack(data[:cls.format.size]))
        st_instance.attributes = []
        st_instance.old_message = rest.encode('string_escape')
        return st_instance
    
    def __init__(self, error_code):
        self.error_code = error_code
        
    def pack(self):
        self.format.pack(self.error_code)
        
    def is_error(self):
        return bool(self.error_code)
        
ServiceTemplate.register(ACK, (NLMSG_ERROR,))

class Attr(object):
    """Represents a single attribute."""
    #struct rtattr {
    #   unsigned short rta_len;    /* Length of option */
    #   unsigned short rta_type;   /* Type of option */
    #   /* Data follows */
    #};
    
    rtattr = Struct('HH')
    
    @classmethod
    def unpack(cls, data):
        length, type = cls.rtattr.unpack(data[:cls.rtattr.size])
        data_len = length-cls.rtattr.size
        attr_data = struct.unpack('{0}s'.format(data_len),
                             data[cls.rtattr.size:cls.rtattr.size+data_len])[0]
        return cls(type, attr_data), data[align(length):]
    
    def __init__(self, rta_type, payload):
        self.rta_type = rta_type
        self.payload = payload
        self.data = self.unpack_data()
        
    def pack(self):
        data = struct.pack('{0}s'.format(len(self.payload)), self.payload)
        rta_len = self.rtattr.size+len(data)
        return struct.pack('{0}{1}s'.format(self.rtattr.format, align(len(data))),
                           rta_len, self.rta_type, data)
    
    def unpack_data(self):
        if hasattr(self, 'data_format') and hasattr(self, 'data_struct'):
            return self.data_struct._make(self.data_format.unpack(self.payload))
        return None
    
    def __repr__(self):
        return """<rtattr datalen=%d rta_type=%d data="%s">""" % (
            align(len(self.payload)), self.rta_type,
            self.payload.encode('string_escape'))

    