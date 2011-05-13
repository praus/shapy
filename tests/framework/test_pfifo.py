import unittest

from shapy.framework.qdisc import pfifoQdisc
from shapy.framework.interface import Interface
from shapy.framework.executor import run

from tests import TCTestCase

class TestPfifo(TCTestCase):
    def setUp(self):
        self.interface = Interface('lo')
        self.pf = pfifoQdisc('1:')
        self.interface.add(self.pf)
        self.interface.set_shaping()
    
    def test_pfifo(self):
        out = run('tc qdisc show dev lo')
    
    def tearDown(self):
        self.interface.teardown()