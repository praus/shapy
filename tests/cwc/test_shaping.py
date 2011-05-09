#import logging
#logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
#                    format='%(asctime)s %(levelname)s: %(message)s')

import unittest
import SocketServer, socket
import random, time
import threading
import cStringIO
from datetime import datetime

from shapy import register_settings
register_settings('tests.cwc.settings')
from shapy.emulation.shaper import Shaper
from mixins import ShaperMixin, ServerMixin
from tests.utils import total_seconds

class TestCWCShaping(unittest.TestCase, ShaperMixin, ServerMixin):
    filesize = 2**19    # 0.5MB
    
    def setUp(self):
        self.server_addr = ('127.0.0.2', 55000)
        self.client_addr = ('127.0.0.3', 55001)
        
        # shaping init
        ShaperMixin.setUp(self)
        
        ServerMixin.run_server(self)

        with open('/dev/urandom', 'rb') as f:
             self.randomfile = bytearray(f.read(self.filesize))
    
    
    def test_transfer(self):
        self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR: http://stackoverflow.com/questions/3229860/what-is-the-meaning-of-so-reuseaddr-setsockopt-option-linux
        s = self.sock_client
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.client_addr)
        s.connect(self.server_addr)
        start = datetime.now()
        
        # client -> server
        sent = 0
        while sent < self.filesize:
            sent += s.send(self.randomfile[sent:sent+4096])
        
        # We have to wait until the server finishes reading data from its socket
        # and closes the connection.
        rcvd = s.recv(1024)
        
        delay = total_seconds(datetime.now() - start)
        #delay = delta.seconds + delta.microseconds/float(10**6)
        tt = self.estimate_transfer_time(self.filesize, self.client_addr[0],
                                         self.server_addr[0])
        self.assertAlmostEqual(delay, tt, delta=0.4)
        
        # server -> client
        start = datetime.now()
        
        while len(rcvd) < self.filesize:
            rcvd += s.recv(1024)
        
        delay = total_seconds(datetime.now() - start)
        tt = self.estimate_transfer_time(self.filesize, self.server_addr[0],
                                         self.client_addr[0])
        self.assertAlmostEqual(delay, tt, delta=0.4)
        
        # statistics of qdiscs on IFB must correctly reflect the transmitted data
        self._test_traffic()
        
        s.close()
    
    def _test_traffic(self):
        c = self.sh.get_traffic(self.client_addr[0])
        s = self.sh.get_traffic(self.server_addr[0])
        # qdisc statistics reflect all traffic, including header of each layer,
        # not only filesize
        delta = self.filesize/100
        self.assertAlmostEqual(c[0], self.filesize, delta=delta)
        self.assertAlmostEqual(c[1], self.filesize, delta=delta)
        self.assertAlmostEqual(s[0], self.filesize, delta=delta)
        self.assertAlmostEqual(s[1], self.filesize, delta=delta)
        
    
    def tearDown(self):
        if hasattr(self, 'sock_client'):
            self.sock_client.close()
        ShaperMixin.tearDown(self)
        