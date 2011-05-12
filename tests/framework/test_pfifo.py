import unittest

from shapy.framework.qdisc import pfifoQdisc
from shapy.framework.interface import Interface
from shapy.framework.executor import run

class TestPfifo(unittest.TestCase):
    def setUp(self):
        self.i = Interface('lo')
        self.pf = pfifoQdisc('1:')
        self.i.add(self.pf)
        self.i.set_shaping()
    
    def test_pfifo(self):
        out = run('tc qdisc show dev lo')
        print out