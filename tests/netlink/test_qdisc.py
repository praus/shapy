import unittest
import socket
import time

from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.connection import Connection
from shapy.framework.netlink.htb import HTBQdiscAttr
from shapy.framework.netlink.netem import NetemOptions
from shapy.framework.utils import nl_us2ticks

from tests.mixins import TeardownMixin

class TestQdisc(unittest.TestCase, TeardownMixin):
    def setUp(self):
        self.if_index = 1   # lo
        self.conn = Connection()
        try:
            self.delete_root_qdisc()
        except OSError:
            pass
    
    def test_add_pfifo_qdisc(self):
        handle = 0x1 << 16 # | 0x1   # major:minor
        tcm = tcmsg(socket.AF_UNSPEC, self.if_index, handle, TC_H_ROOT, 0,
                   [Attr(TCA_KIND, 'pfifo\0')])
        
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)

        self.conn.send(msg)
        self.check_ack(self.conn.recv())
        
        self.delete_root_qdisc()
        
    def test_add_htb_qdisc(self):
        handle = 0x1 << 16 # | 0x1   # major:minor
        tcm = tcmsg(socket.AF_UNSPEC, self.if_index, handle, TC_H_ROOT, 0,
                   [Attr(TCA_KIND, 'htb\0'), HTBQdiscAttr(defcls=0x1ff)])
        
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        self.check_ack(self.conn.recv())
        
        self.delete_root_qdisc()
        
    def test_add_netem_qdisc(self):
        handle = 0x1 << 16 # | 0x1   # major:minor
        delay = nl_us2ticks(500*1000)
        tcm = tcmsg(socket.AF_UNSPEC, self.if_index, handle, TC_H_ROOT, 0,
                   [Attr(TCA_KIND, 'netem\0'), NetemOptions(delay)])
        
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        self.conn.send(msg)
        self.check_ack(self.conn.recv())

        self.delete_root_qdisc()
    
    def check_ack(self, ack):
        self.assertIsInstance(ack.service_template, ACK)
        self.assertEquals(ack.type, 2)
        self.assertEquals(ack.flags, 0x0)