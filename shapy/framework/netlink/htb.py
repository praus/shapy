from shapy.framework.netlink.message import Attr
from .constants import *
from struct import Struct
from shapy.framework.utils import nl_us2ticks

class HTBQdiscAttr(Attr):
    """Representation of HTB qdisc options."""
    #struct tc_htb_glob {
    #    __u32 version;      /* to match HTB/TC */
    #    __u32 rate2quantum; /* bps->quantum divisor */
    #    __u32 defcls;       /* default class number */
    #    __u32 debug;        /* debug flags */
    #
    #    /* stats */
    #    __u32 direct_pkts; /* count of non shapped packets */
    #};
    
    data_format = Struct('6I')
    
    def __init__(self, defcls, r2q=10):
        data = self.data_format.pack(0x20018, 3, r2q, defcls, 0, 0)
        Attr.__init__(self, TCA_OPTIONS, data)


class HTBParms(Attr):
    """
    Internal units: bytes
    """
    #struct tc_ratespec {
    #    unsigned char   cell_log;
    #    unsigned char   __reserved;
    #    unsigned short  overhead;
    #    short       cell_align;
    #    unsigned short  mpu;
    #    __u32       rate;
    #};
    #struct tc_htb_opt {
    #    struct tc_ratespec  rate;
    #    struct tc_ratespec  ceil;
    #    __u32   buffer;
    #    __u32   cbuffer;
    #    __u32   quantum;
    #    __u32   level;      /* out only */
    #    __u32   prio;
    #};
    
    tc_ratespec = Struct("BxHhHI")
    tc_htb_opt = Struct("12x12x5I")
    data_format = Struct("8xI8xI5I") # tc_htb_opt
    
    @classmethod
    def unpack(cls, data):
        attr, rest = Attr.unpack(data)
        d = cls.data_format.unpack(attr.data)
        return cls(d[0], d[1], d[5], d[7])
    
    def __init__(self, rate, ceil, quantum=0, prio=0):
        r = self.tc_ratespec.pack(3, 0, -1, 0, rate)
        c = self.tc_ratespec.pack(3, 0, -1, 0, ceil)
        t = self.tc_htb_opt.pack(390625000, 195312500, quantum, 0, prio)
        data = r + c + t
        Attr.__init__(self, TCA_HTB_PARMS, data)


def tc_calc_rtable(rate, mpu, cell_log, mtu):
    rtab = []
    bps = rate
    
    if mtu == 0:
        mtu = 2047

    if cell_log < 0:
        cell_log = 0;
        n = mtu >> cell_log
        while n > 255:
            cell_log += 1
            n = mtu >> cell_log

    for i in range(0, 256):
        size = (i + 1) << cell_log
        rtab.append(tc_calc_xmittime(bps, size))
        
    return rtab;

def tc_calc_xmittime(rate, size):
    TIME_UNITS_PER_SEC = 1000
    return nl_us2ticks(TIME_UNITS_PER_SEC*(float(size)/rate))

