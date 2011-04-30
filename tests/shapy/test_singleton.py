import unittest2
from shapy.tcelements import *

class TestSingletons(unittest2.TestCase):

    def test_interface_singleton(self):
        self.assertEqual(id(Interface('eth0')), id(Interface('eth0')))
        self.assertNotEqual(id(Interface('eth0')), id(Interface('eth1')))
