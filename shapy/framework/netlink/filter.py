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
    data_struct = Struct(tc_u32_sel.format+tc_u32_key.format)
    
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
        print val
        sel = self.tc_u32_sel.pack(flags, 0, nkeys, 0, 0, 0, 0, 0)
        key = self.tc_u32_key.pack(mask, val, offset, offmask)
        data = sel+key
        super(u32_selector, self).__init__(TCA_U32_SEL, data)