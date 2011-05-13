import unittest
import socket
from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.htb import HTBQdiscAttr
from shapy.framework.netlink.connection import Connection

from tests import TCTestCase

class TestFilter(TCTestCase):
    pass
    #def test_add_filter(self):
    #    self.add_htb_qdisc()
    #    
    #    tcm = tcmsg(socket.AF_UNSPEC, self.if_index, handle, TC_H_ROOT, 0,
    #               [Attr(TCA_KIND, 'htb\0'), HTBQdiscAttr(defcls=0x1ff)])
    #    
    #    msg = Message(type=RTM_NEWTFILTER,
    #                  flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
    #                  service_template=tcm)
    #    
    #    print self.delete_root_qdisc()
    #
    #def add_htb_qdisc(self):
    #    handle = 0x1 << 16 # | 0x1   # major:minor, 1:
    #    tcm = tcmsg(socket.AF_UNSPEC, self.if_index, handle, TC_H_ROOT, 0,
    #               [Attr(TCA_KIND, 'htb\0'), HTBQdiscAttr(defcls=0x1ff)])
    #    
    #    msg = Message(type=RTM_NEWQDISC,
    #                  flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
    #                  service_template=tcm)
    #    
    #    self.conn.send(msg)
    #    print self.conn.recv()
        
        
        
        
        