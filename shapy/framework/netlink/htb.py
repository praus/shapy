import os
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
    tc_htb_opt = Struct("5I")
    data_format = Struct("8xI8xI5I") # tc_htb_opt
    
    @classmethod
    def unpack(cls, data):
        attr, rest = Attr.unpack(data)
        d = cls.data_format.unpack(attr.data)
        return cls(d[0], d[1], d[5], d[7])
    
    def __init__(self, rate, ceil=0, mtu=1600, quantum=0, prio=0):
        """
        rate, ceil, mtu: bytes
        """
        if not ceil: ceil = rate
        r = self.tc_ratespec.pack(3, 0, -1, 0, rate)
        c = self.tc_ratespec.pack(3, 0, -1, 0, ceil)
        hz = os.sysconf('SC_CLK_TCK')
        buffer = tc_calc_xmittime(rate, (rate / hz) + mtu)
        cbuffer = tc_calc_xmittime(ceil, (rate / hz) + mtu)
        t = self.tc_htb_opt.pack(buffer, cbuffer, quantum, 0, prio)
        data = r + c + t
        Attr.__init__(self, TCA_HTB_PARMS, data)


class RTab(Attr):
    """
    Rate table attribute, 256 integers representing an estimate how long it
    takes to send packets of various lengths.
    """
    data_format = Struct("256I")
    
    def __init__(self, rate, mtu, cell_log=3):
        rtab = tc_calc_rtable(rate, cell_log, mtu)
        data = self.data_format.pack(*rtab)
        Attr.__init__(self, TCA_HTB_RTAB, data)
    
class CTab(RTab):
    def __init__(self, rate, mtu, cell_log=3):
        rtab = tc_calc_rtable(rate, cell_log, mtu)
        data = self.data_format.pack(*rtab)
        Attr.__init__(self, TCA_HTB_CTAB, data)
        

def tc_calc_rtable(rate, cell_log, mtu):
    """
    rtab[pkt_len>>cell_log] = pkt_xmit_time
    
    cell - The cell size determines he granularity of packet transmission time
    calculations. Has a sensible default.
    
    """
    # http://kerneltrap.org/mailarchive/linux-netdev/2009/11/2/6259456/thread
    rtab = []
    bps = rate
    
    if mtu == 0:
        mtu = 2047

    if cell_log < 0:
        cell_log = 0
        while (mtu >> cell_log) > 255:
            cell_log += 1

    for i in range(0, 256):
        size = (i + 1) << cell_log
        rtab.append(tc_calc_xmittime(bps, size))
        
    return rtab;

def tc_calc_xmittime(rate, size):
    TIME_UNITS_PER_SEC = 1000000#000
    return int(nl_us2ticks(int(TIME_UNITS_PER_SEC*(float(size)/rate))))

