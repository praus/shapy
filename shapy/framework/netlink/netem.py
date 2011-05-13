
from struct import Struct
from collections import namedtuple

from shapy.framework.netlink.message import Attr
from shapy.framework.utils import nl_ticks2us, nl_us2ticks
from .constants import *



class NetemOptions(Attr):
    #struct tc_netem_qopt {
    #    __u32   latency;    /* added delay (us) */
    #    __u32   limit;      /* fifo limit (packets) */
    #    __u32   loss;       /* random packet loss (0=none ~0=100%) */
    #    __u32   gap;        /* re-ordering gap (0 for none) */
    #    __u32   duplicate;  /* random packet dup  (0=none ~0=100%) */
    #    __u32   jitter;     /* random jitter in latency (us) */
    #};
    
    data_format = Struct("6I")
    data_struct = namedtuple('tc_netem_qopt',
                             "latency limit loss gap duplicate jitter")
    
    @classmethod
    def unpack(cls, data):
        attr, rest = Attr.unpack(data)
        opts = cls.data_struct._make(cls.data_format.unpack(attr.payload))
        opts = opts._replace(latency=nl_ticks2us(opts.latency))
        return cls(*opts)
    
    def __init__(self, latency, limit=1000, loss=0, gap=0, duplicate=0, jitter=0):
        """Latency is in microseconds [us]"""
        latency_ticks = nl_us2ticks(latency)
        data = self.data_format.pack(latency_ticks, limit, loss,
                                     gap, duplicate, jitter)
        Attr.__init__(self, TCA_OPTIONS, data)
