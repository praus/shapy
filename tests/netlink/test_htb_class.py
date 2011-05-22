import unittest
import socket
import os
from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.htb import *
from shapy.framework.netlink.connection import Connection

from tests import TCTestCase

class TestClass(TCTestCase):
    
    def test_add_class(self):
        self.qhandle = 0x1 << 16 # | 0x1   # major:minor, 1:
        self.add_htb_qdisc()
        
        handle = 0x1 << 16 | 0x1
        rate = 256*1000
        mtu = 1600
        
        this_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(this_dir, 'htb_add_class.data'), 'rb') as f:
            data = f.read()
        
        #init = Attr(TCA_HTB_INIT, HTBParms(rate, rate).pack()+data[36+8+4+48:])
        
        init = Attr(TCA_HTB_INIT,
                    HTBParms(rate, rate).pack() +
                    RTab(rate, mtu).pack() + CTab(rate, mtu).pack())
        
        tcm = tcmsg(socket.AF_UNSPEC, self.interface.if_index, handle, self.qhandle, 0,
                   [Attr(TCA_KIND, 'htb\0'), init])
        
        msg = Message(type=RTM_NEWTCLASS,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        self.check_ack(self.conn.recv())

        self.delete_root_qdisc()
    
    def add_htb_qdisc(self):
        tcm = tcmsg(socket.AF_UNSPEC, self.interface.if_index, self.qhandle, TC_H_ROOT, 0,
                   [Attr(TCA_KIND, 'htb\0'), HTBQdiscAttr(defcls=0x1ff)])
        
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        r = self.conn.recv()
        self.check_ack(r)
        return r
        
        
        
        
        