import socket
from shapy.framework.executor import Executable
from .connection import Connection
from .message import Message, Attr
from .tc import tcmsg
from .constants import *
from shapy.framework.utils import convert_handle

connection = Connection()

class NetlinkExecutable(Executable):
    def execute(self):
        c = self.get_context()
        interface = self.get_interface()
        handle = convert_handle(self['handle'])
        
        try:
            parent = convert_handle(c['parent'])
        except ValueError:
            parent = TC_H_ROOT
        
        info = getattr(self, 'tcm_info', 0)
        tcm = tcmsg(socket.AF_UNSPEC, interface.if_index, handle, parent, info,
                    self.attrs)
        msg = Message(type=self.type,
                      flags=NLM_F_EXCL | NLM_F_CREATE | NLM_F_REQUEST | NLM_F_ACK,
                      service_template=tcm)
        
        connection.send(msg)
        resp = connection.recv()
        return resp
