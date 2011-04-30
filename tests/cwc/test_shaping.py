#import logging
#logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
#                    format='%(asctime)s %(levelname)s: %(message)s')

import unittest2
import SocketServer, socket
import random, time
import threading
import cStringIO
from datetime import datetime

from shapy import register_settings
register_settings('tests.cwc.settings')
from cwc.shaper import Shaper
from mixins import ShaperMixin, ServerMixin
from tests.utils import total_seconds

class TestCWCShaping(unittest2.TestCase, ShaperMixin, ServerMixin):
    filesize = 2**19    # 0.5MB
    batchsize = 2**12
    
    def setUp(self):
        self.server_addr = ('127.0.0.2', 55000)
        self.client_addr = ('127.0.0.3', 55001)
        
        # shaping init
        ShaperMixin.setUp(self)
        
        ServerMixin.run_server(self)
        
        #class TestServer(SocketServer.TCPServer):
        #    allow_reuse_address = True
        #
        #class TCPHandler(SocketServer.StreamRequestHandler):
        #    def handle(self):
        #        time_start = datetime.now()
        #        buffer = bytearray()
        #        red = 0
        #        while red < TestCWCShaping.filesize:
        #            r = self.request.recv(TestCWCShaping.batchsize)
        #            buffer.extend(r)
        #            red += len(r)
        #            #print r.encode('hex')
        #        #print "STOP", red,
        #        #import pdb; pdb.set_trace()
        #        delta = datetime.now() - time_start
        #        delay = delta.seconds + delta.microseconds/float(10**6)
        #        print delay,
        #
        #self.ts = TestServer(self.server, TCPHandler)
        #t = threading.Thread(target=self.ts.serve_forever)
        #t.setDaemon(True)
        #t.start()

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
        
        s.close()
        
        print self.sh.get_traffic(self.client_addr[0])
        
    
    def tearDown(self):
        if hasattr(self, 'sock_client'):
            self.sock_client.close()
        ShaperMixin.tearDown(self)
        