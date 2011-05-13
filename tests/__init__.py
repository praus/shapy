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
        try:
            # TODO: delete_ingress_qdisc
            self.delete_root_qdisc()
        except OSError:
            pass
    
    def delete_root_qdisc(self):
        """
        Deletes root egress qdisc on a interface designated by self.if_index
        and returns the resulting ACK message.
        """
        if_index = getattr(self, 'if_index', self.interface.if_index)
        tm = tcmsg(socket.AF_UNSPEC, if_index, 0, TC_H_ROOT, 0)
        msg = Message(type=RTM_DELQDISC,
                      flags=NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tm)
        self.conn.send(msg)
        return self.conn.recv()
    
    def tearDown(self):
        self.delete_root_qdisc()