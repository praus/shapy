from shapy.framework.executor import Executable, get_command
from shapy.framework.mixin import ChildrenMixin, FilterMixin, ClassFilterMixin
from shapy.framework.filter import Filter
from shapy import settings

from shapy.framework.netlink.constants import *
from shapy.framework.netlink import NetlinkExecutable
from shapy.framework.netlink.message import Attr
from shapy.framework.netlink.htb import HTBQdiscAttr
from shapy.framework.netlink.netem import NetemOptions
from shapy.framework.netlink.prio import PrioQdiscAttr

class Qdisc(NetlinkExecutable):
    type = RTM_NEWQDISC
    attrs = []
    
    def __init__(self, handle, **kwargs):
        Executable.__init__(self, **kwargs)
        self.opts.update({'handle': handle})


class QdiscClassless(Qdisc, FilterMixin):
    def __init__(self, *args, **kwargs):
        Qdisc.__init__(self, *args, **kwargs)
        FilterMixin.__init__(self)

class pfifoQdisc(QdiscClassless):
    attrs = [Attr(TCA_KIND, 'pfifo\0')]

class IngressQdisc(QdiscClassless):
    attrs = [Attr(TCA_KIND, 'ingress\0')]
    
    def __init__(self, handle='ffff:', **kwargs):
        QdiscClassless.__init__(self, handle, **kwargs)
    
    def get_context(self):
        return {'interface': self.interface,
                'parent': TC_H_INGRESS}

class NetemDelayQdisc(QdiscClassless):
    def __init__(self, handle, latency, **kwargs):
        self.attrs = [Attr(TCA_KIND, 'netem\0'),
                      NetemOptions(latency*1000)]
        QdiscClassless.__init__(self, handle, **kwargs)


class QdiscClassful(Qdisc, ClassFilterMixin):
    def __init__(self, *args, **kwargs):
        Qdisc.__init__(self, *args, **kwargs)
        ChildrenMixin.__init__(self)

class HTBQdisc(QdiscClassful):
    attrs = [Attr(TCA_KIND, 'htb\0'),
             HTBQdiscAttr(defcls=settings.HTB_DEFAULT_CLASS)]
    #def get(self):
    #    """
    #    A slightly more complicated get method to distinguish between root
    #    qdisc and normal qdisc.
    #    """
    #    self.opts.update(self.get_context())
    #    if hasattr(self, 'interface'):
    #        return get_command('HTBRootQdisc', interface=self.interface,
    #                           default_class=settings.HTB_DEFAULT_CLASS)
    #    
    #    return self.cmd.format(**self.opts)
        
class PRIOQdisc(QdiscClassful):
    attrs = [Attr(TCA_KIND, 'prio\0'), PrioQdiscAttr()]
