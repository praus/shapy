import unittest

from shapy.framework.tcelements import *
from shapy.framework.executor import run

from tests import TCTestCase

class TestIngress(TCTestCase):
    def setUp(self):
        self.interface = Interface('lo')
    
    def test_ingress_filter(self):
        q = IngressQdisc()
        q.add(RedirectFilter('dst 127.0.0.3', 'eth0'))
        self.interface.add_ingress(q)
        self.interface.set_shaping()
