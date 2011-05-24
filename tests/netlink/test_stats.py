import unittest

from shapy.framework.tcelements import *
from shapy.framework.netlink.stats import *


class TestStats(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_class_stats(self):
        data = get_stats(1, RTM_GETTCLASS)
        #print data.encode('string_escape')
        #print len(data)
