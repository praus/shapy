from struct import Struct
from .message import ServiceTemplate
from .constants import *

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

    def __init__(self, tcm_family, tcm_ifindex, tcm_handle, tcm_parent, tcm_info,
                 attributes=[]):
        self.tcm_family = tcm_family
        self.tcm_ifindex = tcm_ifindex
        self.tcm_handle = tcm_handle
        self.tcm_parent = tcm_parent
        self.tcm_info = tcm_info
        self.attributes = attributes
    
    def pack(self):
        tm = tcmsg.format.pack(self.tcm_family, self.tcm_ifindex,
                               self.tcm_handle, self.tcm_parent, self.tcm_info)
        return tm + self.pack_attrs()

    def __repr__(self):
        return "<tcmsg family={0} if={1} handle={2:#x} parent={3:#x} info={4:#x}>".format(
            self.tcm_family, self.tcm_ifindex, self.tcm_handle,
            self.tcm_parent, self.tcm_info)


ServiceTemplate.register(tcmsg, (RTM_NEWQDISC, RTM_DELQDISC, RTM_GETQDISC,
                                 RTM_NEWTCLASS, RTM_DELTCLASS, RTM_GETTCLASS,
                                 RTM_NEWTFILTER, RTM_DELTFILTER, RTM_GETTFILTER))
