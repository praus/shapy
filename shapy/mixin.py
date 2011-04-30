

class ChildrenMixin(object):
    def __init__(self):
        self.children = []
    
    def add(self, child):
        child.parent = self
        self.children.append(child)

class FilterMixin(ChildrenMixin):
    def add(self, child):
        from shapy.filter import Filter
        assert isinstance(child, Filter), \
                        "%s can contain only filters." % self.__class__.__name__
        ChildrenMixin.add(self, child)

class ClassFilterMixin(ChildrenMixin):
    def add(self, child):
        from shapy.filter import Filter
        from shapy.tcclass import TCClass
        assert isinstance(child, (TCClass, Filter)), \
            "%s can contain only filters or classes, not qdiscs." % self.__class__.__name__
        ChildrenMixin.add(self, child)
