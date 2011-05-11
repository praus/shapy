import threading
import socket
from datetime import datetime
import time

from shapy.emulation.shaper import Shaper
from tests.utils import total_seconds, eta

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
        units for filesize are bytes, a and b are IP addresses
        """
        up = self.shaper_conf[(a,)]['upload']
        down = self.shaper_conf[(b,)]['download']
        return eta(filesize, up, down)
        
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

            sent = 0
            while sent < self.filesize:
                sent += conn.send(data[sent:sent+4096])
            
            conn.recv(1)
            conn.close()
            s.close()
        
    def run_server(self):
        self.server_thread = ServerMixin.Server(self.server_addr, self.filesize)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.1) # wait for server to initialize


class ClientMixin(object):
    """
    Expected members of a class this object is mixed into:
    randomfile: the array to be transmitted over the "virtual network"
    filesize: size of transferred file in bytes
    server_addr: (address,port) of a server the client will connect to
    client_addr: (address,port) the client will bind to
    """
    
    def make_transfer(self):
        self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR: http://stackoverflow.com/questions/3229860/what-is-the-meaning-of-so-reuseaddr-setsockopt-option-linux
        s = self.sock_client
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.client_addr)
        s.connect(self.server_addr)
        start = datetime.now()
        
        ## client -> server
        sent = 0
        while sent < self.filesize:
            sent += s.send(self.randomfile[sent:sent+4096])
        
        # We have to wait until the server finishes reading data from its socket
        # and closes the connection.
        rcvd = s.recv(1)
        time_up = total_seconds(datetime.now() - start)
        
        time.sleep(1) # wait for a bucket to fill again
        
        ## server -> client
        start = datetime.now()
        
        while len(rcvd) < self.filesize:
            rcvd += s.recv(1024)
        
        time_down = total_seconds(datetime.now() - start)
        s.close()
        return time_up, time_down
