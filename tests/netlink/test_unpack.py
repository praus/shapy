import os
import unittest
import socket
import struct
from struct import Struct

from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.connection import Connection
from shapy.framework.netlink.netem import *
from shapy.framework.utils import nl_us2ticks

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
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'htb_add_class.data'), 'rb') as f:
            data = f.read()
        msg = Message.unpack(data)
        self.assertEqual(msg.type, RTM_NEWTCLASS)
        self.assertEqual(msg.flags, 0x605)
        
        st = msg.service_template
        self.assertEqual(st.tcm_handle, 0x10005)
        self.assertEqual(st.tcm_parent, 0x10001)
        
        init = tuple(st.unpack_attrs(data[36:]))[1]
        attrs = list(st.unpack_attrs(init.payload))
        self.assertEqual(len(attrs), 3)

    
    #def test_unpack_add_filter(self):
    #    """
    #    tc filter add dev lo parent 1: protocol ip prio 1 u32 \
    #    match ip src 127.0.0.3 flowid 1:5
    #    """
    #    data = "\\\0\0\0,\0\5\6\250\251\313M\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\1\0\10\0\1\0\10\0\1\0u32\0000\0\2\0\10\0\1\0\5\0\1\0$\0\5\0\1\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\377\377\177\0\0\3\f\0\0\0\0\0\0\0"
    #    msg = Message.unpack(data)
    #    print msg
    #    st = msg.service_template
    #    print st.attributes
    
    def test_unpack_add_netem(self):
        """tc qdisc add dev lo root handle 1: netem delay 10ms"""
        data = "\x4c\x00\x00\x00\x24\x00\x05\x06\x07\x1b\xcc\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff\xff\xff\x00\x00\x00\x00\x0a\x00\x01\x00\x6e\x65\x74\x65\x6d\x00\x00\x00\x1c\x00\x02\x00\x5a\x62\x02\x00\xe8\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        msg = Message.unpack(data)
        self.assertEqual(msg.type, RTM_NEWQDISC)
        self.assertEqual(msg.flags, 0x605)

        st = msg.service_template
        self.assertAlmostEqual(st.tcm_handle, 0x10000)
        self.assertAlmostEqual(st.tcm_parent, 0xffffffff)
        
        n = NetemOptions.unpack(data[-28:])
        self.assertEqual(n.data.latency, nl_us2ticks(10*1000))
        

if __name__ == '__main__':
    unittest.main()
