import threading
import socket
from datetime import datetime
import time

from cwc.shaper import Shaper

class ShaperMixin(object):
    def setUp(self):       
        self.shaper_conf = {
            (self.server_addr[0],) : {'upload': 256, 'download': 1024, 'delay': 5},
            (self.client_addr[0],) : {'upload': 128, 'download': 512, 'delay': 30},
        }
        self.sh = Shaper()
        self.sh.set_shaping(self.shaper_conf)
    
    def tearDown(self):
        self.sh.teardown_all()
        
    def estimate_transfer_time(self, filesize, a, b):
        """
        Determines how long the transfer of filesize bytes from A to B should take.
        units for filesize are bytes, a and b are kilobytes
        """
        up = self.shaper_conf[(a,)]['upload']
        down = self.shaper_conf[(b,)]['download']
        return filesize/(min(up, down)*1024)
        
    def estimate_delay(self, a, b):
        da = self.shaper_conf[(a,)]['delay']
        db = self.shaper_conf[(b,)]['delay']
        return da+db

class ServerMixin(object):
    """
    Expected members of a class this object is mixed into:
    filesize: size of transferred file in bytes
    server_addr: (address,port) the server should bind to
    """    
    class Server(threading.Thread):
        def __init__(self, server, filesize):
            threading.Thread.__init__(self)
            self.server_addr = server
            self.filesize = filesize
        
        def run(self):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(self.server_addr)
            s.listen(1)
            conn, addr = s.accept()
            data = bytearray()
            while len(data) < self.filesize:
                data += conn.recv(1024)
            
            conn.sendall(data)
            
            #sent = 0
            #while sent < self.filesize:
            #    sent += s.send(data[sent:sent+4096])
            
            conn.recv(1)
            conn.close()
            s.close()
        
    def run_server(self):
        self.server_thread = ServerMixin.Server(self.server_addr, self.filesize)
        self.server_thread.daemon = True
        self.server_thread.start()