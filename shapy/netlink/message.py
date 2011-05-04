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
from shapy.utils import align

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
        mlength, type, flags, seq, pid = Message.nlmsghdr.unpack(msg[:Message.nlmsghdr.size])
        m = Message(type, flags, seq, payload=msg[Message.nlmsghdr.size:])
        #assert mlength==len(m), "Error decoding message, length of received message does not match the length of decoded message."
        return m
    
    def __init__(self, type, flags=0, seq=-1, payload=''):
        """Used for creating Netlink messages."""
        self.type = type
        self.flags = flags
        self.seq = seq 
        self.pid = 0
        self.payload = payload

    def __len__(self):
        """Aligned length of service template message + attributes."""
        return align(self.nlmsghdr.size + len(self.payload))
    
    def pack_header(self):
        return self.nlmsghdr.pack(len(self), self.type, self.flags, self.seq, self.pid)

    def pack(self):
        return self.pack_header() + self.payload
    #
    #def send(self, conn):
    #    if self.seq == -1: 
    #        self.seq = conn.seq()
    #    self.pid = conn.pid
    #    hdr = self.pack_header()
    #    #print str(hdr+self.payload).encode('string_escape')
    #    conn.send(hdr + self.payload)

    def __repr__(self):
        return '<netlink message type=%s, pid=%s, seq=%s, flags=0x%x "%s">' % (
            self.type, self.pid, self.seq, self.flags, quopri.encodestring(self.payload))


class ServiceTemplate(object):
    """Represents the second part of the Netlink message."""
    @classmethod
    def unpack(cls, data):
        return cls(*cls.format.unpack(data[:cls.format.size])), data[cls.format.size:]

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
    
    format = Struct('I')
    
    def __init__(self, error_code):
        self.error_code = error_code
        
    def is_error(self):
        return bool(self.error_code)
        

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
        data = struct.unpack('{0}s'.format(data_len),
                             data[cls.rtattr.size:cls.rtattr.size+data_len])[0]
        data = data.rstrip('\0')
        return cls(type, data), data[cls.rtattr.size+length:]
    
    def __init__(self, rta_type, data):
        self.rta_type = rta_type
        self.data = struct.pack('{0}s'.format(len(data)+1), data)
        self.rta_len = self.rtattr.size+len(self.data)
        
    def pack(self):
        return struct.pack('{0}{1}s'.format(self.rtattr.format, align(len(self.data))),
                           self.rta_len, self.rta_type, self.data)
    
    def __repr__(self):
        return """<rtattr datalen=%d rta_type=%d data="%s">""" % (
            align(len(self.data)), self.rta_type,
            binascii.b2a_qp(self.data, True, False, False))
