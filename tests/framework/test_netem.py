import unittest

from shapy.framework.qdisc import *
from shapy.framework.tcclass import *
from shapy.framework.filter import *
from shapy.framework.interface import *

from tests.utils import ping
from tests.mixins import TeardownMixin

class TestNetemDelay(unittest.TestCase, TeardownMixin):
    def setUp(self):
        self.delay = 50 # ms
        self.interface = Interface('lo')
        self.interface.add(NetemDelayQdisc('1:', self.delay))
        self.interface.set_shaping()
    
    def test_delay(self):
        c = "127.0.0.2"
        s = "127.0.0.3"
        ping(c, s, 1) # ARP
        self.assertAlmostEqual(ping(c, s), self.delay*2, delta=2)