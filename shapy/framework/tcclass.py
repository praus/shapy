from shapy.framework.netlink import NetlinkExecutable
from shapy.framework.netlink.constants import *
from shapy.framework.netlink.message import *
from shapy.framework.netlink.htb import *

from shapy.framework.mixin import ChildrenMixin
from shapy.framework.utils import convert_to_bytes
from shapy import settings

class TCClass(NetlinkExecutable, ChildrenMixin):
    type = RTM_NEWTCLASS
    
    def __init__(self, handle, **kwargs):
        NetlinkExecutable.__init__(self, **kwargs)
        ChildrenMixin.__init__(self)
        self.opts.update({'handle': handle})

class HTBClass(TCClass):
    def __init__(self, handle, rate, ceil=0, mtu=1600):
        if not ceil: ceil = rate
        rate = convert_to_bytes(rate)
        ceil = convert_to_bytes(ceil)
        init = Attr(TCA_HTB_INIT,
                    HTBParms(rate, ceil).pack() +
                    RTab(rate, mtu).pack() + CTab(ceil, mtu).pack())
        self.attrs = [Attr(TCA_KIND, 'htb\0'), init]
        TCClass.__init__(self, handle)
    
    def get_context(self):
        c = TCClass.get_context(self)
        c.update({'units': settings.UNITS})
        return c