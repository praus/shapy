import unittest
import SocketServer, socket
from tests.utils import ping
from tests.mixins import ShaperMixin
import time

from shapy import register_settings
register_settings('tests.emulation.settings')

class TestCWCDelay(unittest.TestCase, ShaperMixin):
    def setUp(self):
        self.server_addr = ('127.0.0.2', 55000)
        self.client_addr = ('127.0.0.3', 55001)
        ShaperMixin.setUp(self)
    
    def test_delay(self):
        c = self.client_addr[0]
        s = self.server_addr[0]
        ping(c, s, 1) # ARP
        est_delay = self.estimate_delay(c, s)
        self.assertAlmostEqual(ping(c, s), est_delay*2, delta=2)
    
    def tearDown(self):
        ShaperMixin.tearDown(self)