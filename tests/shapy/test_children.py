import unittest2
from shapy.tcelements import *

class TestChildrenManipulation(unittest2.TestCase):
    def setUp(self):
        self.lo = Interface('lo')
        self.hq = HTBQdisc('1:', default_class='1ff')
        self.hc = HTBClass('1:1', rate=100, ceil=100)
        
        self.hq.add(self.hc)
        self.lo.add(self.hq)
    
    def test_add_class(self):
        self.assertEquals(self.hq, self.hc.parent)
    
    def test_add_interface(self):
        self.assertEquals(self.hq.interface, self.lo)
    
    def test_get_interface(self):
        self.assertEquals(self.hc.get_interface(), self.lo)
