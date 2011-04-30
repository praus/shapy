from shapy.executor import Executable
from shapy.mixin import ChildrenMixin
from shapy import settings

class TCClass(Executable, ChildrenMixin):
    def __init__(self, handle, **kwargs):
        Executable.__init__(self, **kwargs)
        ChildrenMixin.__init__(self)
        self.opts.update({'handle': handle})

class HTBClass(TCClass):
    def get_context(self):
        c = TCClass.get_context(self)
        c.update({'units': settings.UNITS})
        return c