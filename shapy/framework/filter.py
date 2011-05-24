import socket
import re
from shapy.framework.netlink import NetlinkExecutable
from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.filter import *
from shapy.framework.exceptions import ImproperlyConfigured
from shapy.framework.utils import convert_handle, get_if_index, validate_full_ip

class Filter(NetlinkExecutable):
    type = RTM_NEWTFILTER
    children = [] # filter cannot have children

class U32Filter(Filter):
    """Abstract filter for matching IP address."""
    def __init__(self, match, **kwargs):
        Filter.__init__(self, **kwargs)
        self.attrs = [Attr(TCA_KIND, 'u32\0')]
        
        dir, val = match.split()
        if validate_full_ip(val):
            ip_packed = socket.inet_aton(val)
            val = struct.unpack("I", ip_packed)[0]
        else:
            val = int(val)
        off_map = {'src': 12, 'dst': 16, 'sport': 20, 'dport': 22}
        # A word of warning: IP packet header can have variable length (up to 15
        # 32bit-words), therefore the above sport and dport offsets might be
        # wrong under very specific circumstances. This is wrong according to
        # RFC 791 (IPv4 specs) but tc tool does not solve this problem either.
        try:
            self.selector = u32_selector(val=val,
                                         offset=off_map[dir],
                                         mask=kwargs.pop('mask', 0xffffffff))
        except KeyError:
            raise ImproperlyConfigured("Invalid direction, must be either src or dst")
        
        self.opts.update({'handle': 0x0})

class RedirectFilter(U32Filter):
    """Redirecting traffic to (mainly) IFB devices"""
    def __init__(self, match, ifb, **kwargs):
        U32Filter.__init__(self, match, **kwargs)
        prio = kwargs.get('prio', 2)
        
        protocol = 8 # IP
        self.tcm_info = prio << 16 | protocol
        
        if_index = get_if_index(ifb)
        flow = u32_classid(convert_handle(0x10001))
        action = u32_mirred_action(if_index)
        self.attrs.append(Attr(TCA_OPTIONS,
                               flow.pack()+action.pack()+self.selector.pack()))
        

class FlowFilter(U32Filter):
    """Classifying traffic to classes."""
    def __init__(self, match, flowid, **kwargs):
        U32Filter.__init__(self, match, **kwargs)
        prio = kwargs.get('prio', 3)
        protocol = 8
        self.tcm_info = prio << 16 | protocol
        
        flow = u32_classid(convert_handle(flowid))
        self.attrs.append(Attr(TCA_OPTIONS, flow.pack() + self.selector.pack()))

