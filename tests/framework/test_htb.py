import unittest

from shapy.framework.qdisc import *
from shapy.framework.tcclass import *
from shapy.framework.filter import *
from shapy.framework.interface import *

from tests.utils import ping, random_file, eta
from tests.mixins import ServerMixin, ClientMixin

class TestHTB(unittest.TestCase, ServerMixin, ClientMixin):
    def setUp(self):
        self.server_addr = ('127.0.0.2', 55000)
        self.client_addr = ('127.0.0.3', 55001)
        self.server_speed = 256 # download speed in kbyte/s
        self.client_speed = 128 
        
        self.i = Interface('lo')
        h1 = HTBQdisc('1:', default_class='1ff')
        h1.add( FlowFilter('dst 127.0.0.2', '1:2', prio=1) )
        h1.add( FlowFilter('dst 127.0.0.3', '1:1', prio=1) )
        h1.add( HTBClass('1:1', rate=self.server_speed, ceil=self.server_speed))
        h1.add( HTBClass('1:2', rate=self.client_speed, ceil=self.client_speed))
        self.i.add( h1 )
        self.i.set_shaping()
        
        self.filesize = 2**20
        self.randomfile = random_file(self.filesize)
        
        self.run_server()
    
    def test_shaping(self):
        time_up, time_down = self.make_transfer()
        
        eta = self.filesize/(self.client_speed*1024)
        self.assertAlmostEqual(time_up, eta, delta=1)
        
        eta = self.filesize/(self.server_speed*1024)
        self.assertAlmostEqual(time_down, eta, delta=1)
        
    def tearDown(self):
        self.i.teardown()


