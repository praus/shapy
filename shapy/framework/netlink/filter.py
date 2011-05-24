"""
Please see doc/tc_filter_attr_structure.pdf for figure explaining attribute
structure of TC filter messages.
"""

from shapy.framework.netlink.message import Attr
from .constants import *
from struct import Struct

class u32_classid(Attr):
    data_format = Struct("I")
    
    def __init__(self, classid):
        data = self.data_format.pack(classid)
        super(u32_classid, self).__init__(TCA_U32_CLASSID, data)
        

class u32_selector(Attr):
    #struct tc_u32_sel {
    #    unsigned char       flags;
    #    unsigned char       offshift;
    #    unsigned char       nkeys;
    #
    #    __be16          offmask;
    #    __u16           off;
    #    short           offoff;
    #
    #    short           hoff;
    #    __be32          hmask;
    #    struct tc_u32_key   keys[0];
    #};
    
    #struct tc_u32_key {
    #    __be32      mask;
    #    __be32      val;
    #    int     off;
    #    int     offmask;
    #};
    
    tc_u32_sel = Struct("BBBHHhhI")
    tc_u32_key = Struct("IIii")
    data_format = Struct(tc_u32_sel.format+tc_u32_key.format)
    
    def __init__(self, val, offset, mask=0xffffffff, offmask=0):
        """
        Selector for u32 filter, value is IP address for example.
        offset is 12 (0xc) for source IP, 16 for destination IP.
        
        This is rather crude, underlying kernel infrastructure supports multiple
        keys, but since there was no need for such a functionality, it is left
        out. See iproute2 sources for example how to implement it.
        """
        flags = TC_U32_TERMINAL
        nkeys = 1
        sel = self.tc_u32_sel.pack(flags, 0, nkeys, 0, 0, 0, 0, 0)
        key = self.tc_u32_key.pack(mask, val, offset, offmask)
        data = sel+key
        super(u32_selector, self).__init__(TCA_U32_SEL, data)


class u32_mirred_action(Attr):
    """
    The basic action redirecting all matched traffic to the interface specified
    by ifindex using mirred strategy.
    """
    # include/linux/tc_act/tc_mirred.h
    ##define tc_gen \
    #    __u32                 index; \
    #    __u32                 capab; \
    #    int                   action; \
    #    int                   refcnt; \
    #    int                   bindcnt
    #struct tc_mirred {
    #    tc_gen;
    #    int                     eaction;   /* one of IN/EGRESS_MIRROR/REDIR */
    #    __u32                   ifindex;  /* ifindex of egress port */
    #};
    
    data_format = Struct("IIiiiiI")
    
    def __init__(self, ifindex):
        tc_mirred_parms = Attr(TCA_MIRRED_PARMS,
                               self.data_format.pack(0, 0, TCA_INGRESS_MIRROR, 0, 0,
                                                     TCA_EGRESS_REDIR, ifindex))
        kind = Attr(TCA_ACT_KIND, "mirred\0")
        options = Attr(TCA_ACT_OPTIONS, tc_mirred_parms.pack())
        redir = Attr(TCA_EGRESS_REDIR, kind.pack()+options.pack())
        super(u32_mirred_action, self).__init__(TCA_U32_ACT, redir.pack())
