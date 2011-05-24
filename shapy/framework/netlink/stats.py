import socket
from struct import Struct

from .connection import Connection
from .message import Message, Attr
from .tc import tcmsg
from .constants import *

from shapy.framework.utils import convert_handle

# RTM_GETTCLASS

def get_stats(if_index, type):
    #struct tc_stats {
    #    __u64   bytes;          /* NUmber of enqueues bytes */
    #    __u32   packets;        /* Number of enqueued packets   */
    #    __u32   drops;          /* Packets dropped because of lack of resources */
    #    __u32   overlimits;     /* Number of throttle events when this
    #                     * flow goes out of allocated bandwidth */
    #    __u32   bps;            /* Current flow byte rate */
    #    __u32   pps;            /* Current flow packet rate */
    #    __u32   qlen;
    #    __u32   backlog;
    #};

    tc_stats = Struct("L7I")

    #handle = 0x1 << 16 | 0x1
    handle = 0x0
    tcm = tcmsg(socket.AF_UNSPEC, if_index, handle, TC_H_ROOT, 0,
                attributes=[])
    msg = Message(type=type,
                  flags=NLM_F_ROOT | NLM_F_MATCH | NLM_F_REQUEST,
                  service_template=tcm)
    
    conn = Connection()
    conn.send(msg)
    
    msgs = []
    flags = NLM_F_MULTI
    while flags == NLM_F_MULTI:
        m = conn.recv()
        print m
        msgs.append(m)
        flags = m.flags
        if m.type == NLMSG_DONE:
            break
    
    return msgs
    
    
