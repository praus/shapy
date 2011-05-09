from shapy.framework.netlink.message import Attr
from .constants import *
from struct import Struct


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
