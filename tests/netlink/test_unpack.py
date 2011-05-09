import unittest
import socket
import struct
from struct import Struct

from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.connection import Connection


class TestUnpack(unittest.TestCase):
    def setUp(self):
        self.conn = Connection()
    
    def test_unpack_add_qdisc(self):
        aq = "\x48\x00\x00\x00\x24\x00\x05\x06\x4d\x34\xc1\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff\xff\xff\x00\x00\x00\x00\x08\x00\x01\x00\x68\x74\x62\x00\x1c\x00\x02\x00\x18\x00\x02\x00\x03\x00\x00\x00\x0a\x00\x00\x00\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        
        m = Message.unpack(aq)
        st = m.service_template
        print m
        print st
        print st.attributes
        print '-'*20
        print len(st.attributes[1].data)
        print struct.unpack('6I', st.attributes[1].data)
        
        print Attr.unpack(aq[44:])
    
    #def test_raw_create(self):
    #    self.conn.send(self.test)
    #    print self.conn.recv()


if __name__ == '__main__':
    unittest.main()
