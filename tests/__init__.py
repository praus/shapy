import unittest
import socket

from shapy.framework.netlink.connection import Connection
from shapy.framework.netlink.message import *
from shapy.framework.netlink.tc import *
from shapy.framework.netlink.constants import *
from shapy.framework.interface import Interface

class TCTestCase(unittest.TestCase):
    """
    Generic test case used as a base for testing any Traffic Control components.
    """
    conn = Connection()
    
    def setUp(self):
        self.interface = Interface('lo')
        # clean the environment before we start
        self.tearDown()
    
    def delete_root_qdisc(self):
        """
        Deletes root egress qdisc on a interface designated by self.if_index
        and returns the resulting ACK message.
        """
        if_index = getattr(self, 'if_index', self.interface.if_index)
        tm = tcmsg(socket.AF_UNSPEC, if_index, 0, TC_H_ROOT, 0)
        return self._del_qdisc(tm)
    
    def delete_ingress_qdisc(self):
        """
        Deletes ingress qdisc on a interface designated by self.if_index
        and returns the resulting ACK message.
        """
        if_index = getattr(self, 'if_index', self.interface.if_index)
        tm = tcmsg(socket.AF_UNSPEC, if_index, 0, TC_H_INGRESS, 0)
        return self._del_qdisc(tm)
    
    def _del_qdisc(self, st):
        msg = Message(type=RTM_DELQDISC,
                      flags=NLM_F_REQUEST | NLM_F_ACK,
                      service_template=st)
        self.conn.send(msg)
        return self.conn.recv()
    
    def tearDown(self):
        try:
            self.delete_root_qdisc()
            self.delete_ingress_qdisc()
        except OSError:
            pass