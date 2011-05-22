import unittest
import socket
from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.htb import HTBQdiscAttr
from shapy.framework.netlink.filter import *
from shapy.framework.netlink.connection import Connection

from tests import TCTestCase

class TestFilter(TCTestCase):
    def test_add_filter(self):
        self.add_htb_qdisc()
        
        ip_packed = socket.inet_aton("127.0.0.3")
        
        flow = u32_classid(0x10003)
        sel = u32_selector(val=struct.unpack("I", ip_packed)[0],
                           offset=12)
        
        selector = Attr(TCA_OPTIONS, flow.pack() + sel.pack())
        handle = 0x0
        parent = 0x1 << 16
        prio = 13
        protocol = 8
        info = prio << 16 | protocol
        tcm = tcmsg(socket.AF_UNSPEC, self.interface.if_index, handle, parent, info,
                   [Attr(TCA_KIND, 'u32\0'), selector])
        
        msg = Message(type=RTM_NEWTFILTER,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        print self.conn.recv()
        
        print self.delete_root_qdisc()
    
    def add_htb_qdisc(self):
        handle = 0x1 << 16 # | 0x1   # major:minor, 1:
        tcm = tcmsg(socket.AF_UNSPEC, self.interface.if_index, handle, TC_H_ROOT, 0,
                   [Attr(TCA_KIND, 'htb\0'), HTBQdiscAttr(defcls=0x1ff)])
        
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        print self.conn.recv()

