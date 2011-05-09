from shapy.framework.executor import Executable, get_command
from shapy.framework.mixin import ChildrenMixin, FilterMixin, ClassFilterMixin
from shapy.framework.filter import Filter
from shapy import settings

class Qdisc(Executable):
    def __init__(self, handle, **kwargs):
        Executable.__init__(self, **kwargs)
        self.opts.update({'handle': handle})

class QdiscClassless(Qdisc, FilterMixin):
    def __init__(self, *args, **kwargs):
        Qdisc.__init__(self, *args, **kwargs)
        FilterMixin.__init__(self)

class pfifoQdisc(QdiscClassless):
    pass

class IngressQdisc(QdiscClassless):
    def __init__(self, handle='ffff:', **kwargs):
        QdiscClassless.__init__(self, handle, **kwargs)
    
    def get_context(self):
        return {'interface': self.interface}

class NetemDelayQdisc(QdiscClassless):
    pass


class QdiscClassful(Qdisc, ClassFilterMixin):
    def __init__(self, *args, **kwargs):
        Qdisc.__init__(self, *args, **kwargs)
        ChildrenMixin.__init__(self)

class HTBQdisc(QdiscClassful):
    def get(self):
        """
        A slightly more complicated get method to distinguish between root
        qdisc and normal qdisc.
        """
        self.opts.update(self.get_context())
        if hasattr(self, 'interface'):
            return get_command('HTBRootQdisc', interface=self.interface,
                               default_class=settings.HTB_DEFAULT_CLASS)
        
        return self.cmd.format(**self.opts)
        
class PRIOQdisc(QdiscClassful):
    pass
