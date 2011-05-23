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
    """
    Tests adding TC filters using netlink interface.
    """
    
    def setUp(self):
        super(TestFilter, self).setUp()
        self.qhandle = 0x1 << 16 # | 0x1   # major:minor, 1:
        ip_packed = socket.inet_aton("127.0.0.3")
        self.selector = u32_selector(val=struct.unpack("I", ip_packed)[0],
                                     offset=12)
        self.classid = u32_classid(0x10003)
        
        prio = 13
        protocol = 8
        self.tcm_info = prio << 16 | protocol
    
    def test_add_filter(self):
        self.add_htb_qdisc()

        opts = Attr(TCA_OPTIONS, self.classid.pack() + self.selector.pack())
        self.add_filter(self.tcm_info, [Attr(TCA_KIND, 'u32\0'), opts])
        
    
    def test_add_redirect_filter(self):
        self.add_htb_qdisc()

        action = u32_mirred_action(self.interface.if_index)        
        opts = Attr(TCA_OPTIONS,
                    self.classid.pack() + action.pack() + self.selector.pack())
        self.add_filter(self.tcm_info, [Attr(TCA_KIND, 'u32\0'), opts])
    
    
    def add_filter(self, tcm_info, attrs):
        handle = 0x0
        parent = self.qhandle
        tcm = tcmsg(socket.AF_UNSPEC, self.interface.if_index, handle, parent, tcm_info,
                   attrs)
        
        msg = Message(type=RTM_NEWTFILTER,
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
        self.conn.recv()

