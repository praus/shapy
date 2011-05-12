import unittest
from shapy.framework.tcelements import *

class TestInterface(unittest.TestCase):

    def test_interface_singleton(self):
        self.assertEqual(id(Interface('eth0')), id(Interface('eth0')))
        self.assertNotEqual(id(Interface('eth0')), id(Interface('eth1')))

    def test_ifindex(self):
        # loopback should always have if_index == 1
        self.assertEqual(Interface('lo').if_index, 1)