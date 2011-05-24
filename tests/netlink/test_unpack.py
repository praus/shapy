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
from shapy.framework.netlink.filter import *
from shapy.framework.utils import nl_us2ticks

from tests.utils import *

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
        
        tc class add dev lo parent 1: classid 1:1 htb rate 534
        """
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'htb_add_class.data'), 'rb') as f:
            data = f.read()
        msg = Message.unpack(data)
        self.assertEqual(msg.type, RTM_NEWTCLASS)
        self.assertEqual(msg.flags, 0x605)
        
        st = msg.service_template
        self.assertEqual(st.tcm_handle, 0x10001)
        self.assertEqual(st.tcm_parent, 0x10000)
        
        init = tuple(st.unpack_attrs(data[36:]))[1]
        attrs = list(st.unpack_attrs(init.payload))
        self.assertEqual(len(attrs), 3)
        
        from shapy.framework.netlink.htb import tc_calc_rtable
        self.assertItemsEqual(tc_calc_rtable(66, -1, 1600),
                              struct.unpack("256I", attrs[2].payload),
                              "Rate table (rtab) calculation is wrong.")

    
    def test_unpack_add_filter(self):
        """
        tc filter add dev lo parent 1: protocol ip prio 13 u32 \
        match ip src 127.0.0.3 flowid 1:3
        
        ['0x10008', '0x10003', '0x50024', '0x10001', '0x0', '0x0', '0x0', '0xffffffff', '0x300007f', '0xc', '0x0']
        
        ??, flowid, ??, parent, ??, ??, ??, mask, match, prio, ??
        
        protocol id (IP) (3?)
        offset?
        
        """
        data = "\x5c\x00\x00\x00\x2c\x00\x05\x06\x05\x8e\xce\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x08\x00\x0d\x00\x08\x00\x01\x00\x75\x33\x32\x00\x30\x00\x02\x00\x08\x00\x01\x00\x03\x00\x01\x00\x24\x00\x05\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x7f\x00\x00\x03\x0c\x00\x00\x00\x00\x00\x00\x00"
        msg = Message.unpack(data)
        #print msg
        st = msg.service_template
        attr = st.attributes
        #print st
        #print attr
        
        tc_u32_sel = Struct("BBBHHhhI")
        tc_u32_key = Struct("IIii")
        nested = list(unpack_attrs(attr[1].payload))
        #print nested
        #print "{0:#x}".format(struct.unpack("I", nested[0].payload)[0])
        sel = tc_u32_sel.unpack(nested[1].payload[:16])
        key = tc_u32_key.unpack(nested[1].payload[16:])
        #print [ "{0:#x}".format(a) for a in key ]
        #print key[1]
        #print [ "{0:#x}".format(a) for a in struct.unpack("HH10I", attr[1].payload) ]
        
        #import pdb; pdb.set_trace()
    
    def test_unpack_tcp_filter(self):
        """
        tc filter add dev lo parent 1: protocol ip prio 1 u32 \
        match ip sport 8000 0xffff flowid 1:5
        """
        data = "\\\0\0\0,\0\5\6!\201\333M\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\1\0\10\0\1\0\10\0\1\0u32\0000\0\2\0\10\0\1\0\5\0\1\0$\0\5\0\1\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\0\0\37@\0\0\24\0\0\0\0\0\0\0"
        #data = "\\\0\0\0,\0\5\6\352\210\333M\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\1\0\10\0\1\0\10\0\1\0u32\0000\0\2\0\10\0\1\0\5\0\1\0$\0\5\0\1\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\0\0\37@\24\0\0\0\0\0\0\0"
        msg = Message.unpack(data)
        st = msg.service_template
        attr = st.attributes
        
        tc_u32_sel = Struct("BBBHHhhI")
        tc_u32_key = Struct("IIii")
        nested = list(unpack_attrs(attr[1].payload))
        sel = tc_u32_sel.unpack(nested[1].payload[:16])
        key = tc_u32_key.unpack(nested[1].payload[16:])
        #print sel, key
        #print hex_list(sel), hex_list(key)
    
    def test_unpack_add_redirect_filter(self):
        """
        tc filter add dev lo parent 1: protocol ip prio 3 \
        u32 match ip dst 127.0.0.4 flowid 1:1 \
        action mirred egress redirect dev ifb0
        
        filter parent 1: protocol ip pref 3 u32 
        filter parent 1: protocol ip pref 3 u32 fh 800: ht divisor 1 
        filter parent 1: protocol ip pref 3 u32 fh 800::800 order 2048 key ht 800 bkt 0 flowid 1:1 
          match 7f000004/ffffffff at 16
            action order 1: mirred (Egress Redirect to device ifb0) stolen
            index 2 ref 1 bind 1
        """
        data = "\x94\x00\x00\x00\x2c\x00\x05\x06\x4f\x21\xda\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x08\x00\x01\x00\x75\x33\x32\x00\x68\x00\x02\x00\x08\x00\x01\x00\x01\x00\x01\x00\x38\x00\x07\x00\x34\x00\x01\x00\x0b\x00\x01\x00\x6d\x69\x72\x72\x65\x64\x00\x00\x24\x00\x02\x00\x20\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x24\x00\x05\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x7f\x00\x00\x04\x10\x00\x00\x00\x00\x00\x00\x00"
        msg = Message.unpack(data)
        st = msg.service_template
        attr = st.attributes
        
        tc_u32_sel = Struct("BBBHHhhI")
        tc_u32_key = Struct("IIii")
        filter_opt = list(unpack_attrs(attr[1].payload)) # TCA_KIND, TCA_OPTIONS
        action = list(unpack_attrs(filter_opt[1].payload)) # TCA_EGRESS_REDIR
        mirred = list(unpack_attrs(action[0].payload)) # TCA_ACT_KIND, TCA_ACT_OPTIONS
        mirred_parms = list(unpack_attrs(mirred[1].payload))
        
        tc_mirred = Struct("IIiiiiI")
        #print tc_mirred.unpack(mirred_parms[0].payload)
    
    
    def test_unpack_add_netem(self):
        """tc qdisc add dev lo root handle 1: netem delay 10ms"""
        data = "\x4c\x00\x00\x00\x24\x00\x05\x06\x07\x1b\xcc\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff\xff\xff\x00\x00\x00\x00\x0a\x00\x01\x00\x6e\x65\x74\x65\x6d\x00\x00\x00\x1c\x00\x02\x00\x5a\x62\x02\x00\xe8\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        msg = Message.unpack(data)
        self.assertEqual(msg.type, RTM_NEWQDISC)
        self.assertEqual(msg.flags, 0x605)

        st = msg.service_template
        self.assertAlmostEqual(st.tcm_handle, 0x10000)
        self.assertAlmostEqual(st.tcm_parent, 0xffffffff)
        
        attr, data = NetemOptions.unpack(data[-28:])
        self.assertEqual(attr.data.latency, nl_us2ticks(10*1000))
    
    def test_unpack_add_prio(self):
        data = "\x4c\x00\x00\x00\x24\x00\x05\x06\x67\x9c\xcd\x4d\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00\xff\xff\xff\xff\x00\x00\x00\x00\x09\x00\x01\x00\x70\x72\x69\x6f\x00\x00\x00\x00\x1c\x00\x02\x00\x03\x00\x00\x00\x01\x02\x02\x02\x01\x02\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01\x04\x00\x02\x00"
        msg = Message.unpack(data)
        self.assertEqual(msg.type, RTM_NEWQDISC)
        self.assertEqual(msg.flags, 0x605)
        self.assertEqual(msg.service_template.attributes[1].payload, data[-24:])
    

if __name__ == '__main__':
    unittest.main()
