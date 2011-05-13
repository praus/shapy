from shapy.framework.netlink.message import Attr
from .constants import *
from struct import Struct
from collections import namedtuple


class PrioQdiscAttr(Attr):
    #define TC_PRIO_BESTEFFORT      0
    #define TC_PRIO_FILLER          1
    #define TC_PRIO_BULK            2
    #define TC_PRIO_INTERACTIVE_BULK    4
    #define TC_PRIO_INTERACTIVE     6
    #define TC_PRIO_CONTROL         7
    
    #define TC_PRIO_MAX         15
    
    #define TCQ_PRIO_BANDS  16
    #define TCQ_MIN_PRIO_BANDS 2
    
    #struct tc_prio_qopt {
    #    int bands;          /* Number of bands */
    #    __u8    priomap[TC_PRIO_MAX+1]; /* Map: logical priority -> PRIO band */
    #};

    data_format = Struct("i16B4x")
    data_struct = namedtuple('tc_prio_qopt', "bands priomap")
    
    @classmethod
    def unpack(cls, data):
        attr, rest = Attr.unpack(data)
        data = self.data_format.unpack(attr.payload)
        opts = cls.data_struct._make((data[0], data[1:]))
        return cls(opts.bands, opts.priomap), rest
    
    def unpack_data(self):
        data = self.data_format.unpack(self.payload)
        return self.data_struct._make(self.data_struct._make((data[0], data[1:])))
    
    def __init__(self, bands=3, priomap="1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1"):
        pm = [ int(p) for p in priomap.split() ]
        data = self.data_format.pack(bands, *pm)
        Attr.__init__(self, TCA_OPTIONS, data)