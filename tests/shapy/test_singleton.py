import unittest
from shapy.framework.tcelements import *

class TestSingletons(unittest.TestCase):

    def test_interface_singleton(self):
        self.assertEqual(id(Interface('eth0')), id(Interface('eth0')))
        self.assertNotEqual(id(Interface('eth0')), id(Interface('eth1')))
