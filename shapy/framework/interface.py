import logging
logger = logging.getLogger('shapy.framework.interface')

from shapy.framework import executor, utils

class Interface(object):
    interfaces = {}
    
    def __new__(cls, name):
        if Interface.interfaces.has_key(name):
            return Interface.interfaces[name]
        instance = super(Interface, cls).__new__(cls)
        Interface.interfaces.update({name: instance})
        return instance
    
    def __del__(self):
        del Interface.interfaces[self.name]
    
    def __init__(self, name):
        self.name = name
        self.if_index = utils.get_if_index(self.name)
    
    def __str__(self):
        return self.name
    
    def add(self, root_qdisc):
        self.root = root_qdisc
        self.root.interface = self
        return self.root
        
    def add_ingress(self, ingress_qdisc):
        self.ingress = ingress_qdisc
        self.ingress.interface = self
        return self.ingress
        
    def set_shaping(self):
        #assert self.root, "Interface must contain at least a root qdisc."
        if hasattr(self, 'ingress'):
            self.ingress.execute()
            for ch in self.ingress.children:
                ch.execute()
        if hasattr(self, 'root'):
            self.__traverse_tree(self.root)
    
    def teardown(self):
        """
        Tears down all custom qdiscs, classes and filters on this interface.
        """
        cmd_e = executor.get_command('TCInterfaceTeardown', interface=self.name,
                                   handle='root')
        cmd_i = executor.get_command('TCInterfaceTeardown', interface=self.name,
                                   handle='ingress')
        executor.run(cmd_e)
        executor.run(cmd_i)
        
    def __traverse_tree(self, element):
        logger.debug("Interface '{0!s}' executing {1}"\
                     .format(self, element.__class__.__name__))
        element.execute()
        for ch in element.children:
            self.__traverse_tree(ch)


class IFB(Interface, executor.Executable):
    module_loaded = False
    
    def __init__(self, name):
        executor.Executable.__init__(self)
        self.name = name
        #Interface.__init__(self, name)

    def set_shaping(self):
        self.if_index = utils.get_if_index(self.name)
        self.execute()
        Interface.set_shaping(self)
    
    def get_context(self):
        return {'interface': self.name}
    
    @staticmethod
    def teardown():
        """
        A custom teardown, all we need to do is unload the module
        """
        #Interface.teardown(self)
        if IFB.module_loaded:
            executor.run('rmmod ifb')
            IFB.module_loaded = False
    
    @staticmethod
    def modprobe():
        if not IFB.module_loaded:
            executor.run('modprobe ifb')
            IFB.module_loaded = True
