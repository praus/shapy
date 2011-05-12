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
    
    #def test_unpack_add_qdisc(self):
    #    aq = "\x48\x00\x00\x00\x24\x00\x05\x06\x4d\x34\xc1\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff\xff\xff\x00\x00\x00\x00\x08\x00\x01\x00\x68\x74\x62\x00\x1c\x00\x02\x00\x18\x00\x02\x00\x03\x00\x00\x00\x0a\x00\x00\x00\xff\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    #    
    #    m = Message.unpack(aq)
    #    st = m.service_template
    #    print m
    #    print st
    #    print st.attributes
    #    print '-'*20
    #    print len(st.attributes[1].data)
    #    print struct.unpack('6I', st.attributes[1].data)
    #    
    #    print Attr.unpack(aq[44:])
    
    def test_unpack_htb_class(self):
        """
        TCA_HTB_INIT is composed from TCA_HTB_PARMS, TCA_HTB_CTAB, TCA_HTB_RTAB
        """
        
        with open('tests/netlink/htb_add_class.data', 'rb') as f:
            data = f.read()
        msg = Message.unpack(data)
        
        init = tuple(self.unpack_attrs(data[36:]))[1]
        attrs = [ self.unpack_attrs(init.payload) ]
        #self.assertEqual(len(attrs), 3)

    def unpack_attrs(self, data):
        while True:
            attr, data = Attr.unpack(data)
            yield attr
            if not data: break
    
    def test_unpack_filter(self):
        data = "\\\0\0\0,\0\5\6\250\251\313M\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\1\0\10\0\1\0\10\0\1\0u32\0000\0\2\0\10\0\1\0\5\0\1\0$\0\5\0\1\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\377\377\177\0\0\3\f\0\0\0\0\0\0\0"
        msg = Message.unpack(data)
        print msg
        st = msg.service_template
        print st.attributes

if __name__ == '__main__':
    unittest.main()
