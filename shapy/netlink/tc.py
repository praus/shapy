from struct import Struct
from .message import ServiceTemplate

class tcmsg(ServiceTemplate):
    """
    Traffic Control service template
    http://tools.ietf.org/html/rfc3549#page-21
    """
    #0                   1                   2                   3
    #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|   Family    |  Reserved1    |         Reserved2             |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                     Interface Index                         |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                      Qdisc handle                           |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                     Parent Qdisc                            |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    #|                        TCM Info                             |
    #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    
    #struct tcmsg {
    #    unsigned char    tcm_family;
    #    int              tcm_ifindex;   /* interface index */
    #    __u32            tcm_handle;    /* Qdisc handle */
    #    __u32            tcm_parent;    /* Parent qdisc */
    #    __u32            tcm_info;
    #};
    
    format = Struct("BxxxiIII")

    def __init__(self, tcm_family, tcm_ifindex, tcm_handle, tcm_parent, tcm_info):
        self.tcm_family = tcm_family
        self.tcm_ifindex = tcm_ifindex
        self.tcm_handle = tcm_handle
        self.tcm_parent = tcm_parent
        self.tcm_info = tcm_info
    
    def pack(self):
        return tcmsg.format.pack(self.tcm_family, self.tcm_ifindex,
                                self.tcm_handle, self.tcm_parent, self.tcm_info)

    def __repr__(self):
        return "<tcmsg family={0} if={1} handle={2} parent={3} info={4}>".format(
            self.tcm_family, self.tcm_ifindex, self.tcm_handle,
            self.tcm_parent, self.tcm_info)

TCA_KIND    = 1
TCA_OPTIONS = 2
TCA_STATS   = 3
TCA_XSTATS  = 4
TCA_RATE    = 5
TCA_FCNT    = 6
TCA_STATS2  = 7
TCA_STAB    = 8
