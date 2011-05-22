import unittest
import os, pwd, grp
import socket

from shapy.framework.netlink.constants import *

@unittest.skip("This is just an illustration simply dropping privileges does not work.")
class TestPrivilegeDrop(unittest.TestCase):
    def setUp(self):
        self.if_index = 1
        self.qhandle = 0x1 << 16

    def test_drop(self):
        self.assertEqual(os.getuid(), pwd.getpwnam("root").pw_uid,
                            "You have to be root to run this test")
        
        # import netlink a create a connection as root
        from shapy.framework import netlink
        
        # http://stackoverflow.com/questions/2699907/dropping-root-permissions-in-python
        # drop privileges to nobody
        os.setuid(pwd.getpwnam("nobody").pw_uid)
        #os.setgid(grp.getgrnam("nogroup").gr_gid)
        #os.setgroups([])
        
        # try to do operation on a netlink socket while being an unprivileged user
        from shapy.framework.netlink.message import Message, Attr
        from shapy.framework.netlink.tc import tcmsg
        
        tcm = tcmsg(socket.AF_UNSPEC, self.if_index, self.qhandle, TC_H_ROOT, 0,
                    [Attr(TCA_KIND, 'pfifo\0')])
        msg = Message(type=RTM_NEWQDISC,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        netlink.connection.send(msg)
        
        # and observe we are out of luck :/
        self.assertRaisesRegexp(OSError, "Operation not permitted",
                                netlink.connection.recv)
