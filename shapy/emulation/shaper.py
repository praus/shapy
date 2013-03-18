# -*- coding: utf-8 -*-
"""
CWC shaper using ShaPy Linux TC library. The basic requirement is that it needs
to aggregate traffic on all specified interfaces to IFB devices and shape it
creating an ilussion of real network.

Intermediate Function Block is virtual network device used to shape download
speeds. We will set filter for interface we wish to shape download on to forward
all traffic to IFB. There we can shape it as a standard outgoing (egress)
traffic albeit in reality it is incoming (ingress) traffic.

@author: Petr Praus
"""
import re
import logging
import logging.handlers

from shapy import settings
from shapy.framework import tcelements as shapy
from shapy.framework import executor
from shapy.framework import utils

LOG_FILENAME = 'shaper.log'

shapy_logger = logging.getLogger('shapy')
shapy_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=100*1024, backupCount=5)
fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(fmt)
shapy_logger.addHandler(handler)


logger = logging.getLogger('shapy.emulation.shaper')

class Shaper(object):
    instance = None
    
    def __new__(cls):
        if Shaper.instance:
            return Shaper.instance
        Shaper.instance = super(Shaper, cls).__new__(cls)
        return Shaper.instance
    
    ifb_up = shapy.IFB('ifb1')
    ifb_down = shapy.IFB('ifb0')
    
    # Namespace allocation for handlers:
    # 0x1-0x1FE HTB shapers, 0x1FF default HTB, 0x200 - 0x3FF netem
    # HTB handles
    ifb_up.qhandles = ( '{0:x}'.format(n) for n in xrange(1, 511) )
    ifb_down.qhandles = ( '{0:x}'.format(n) for n in xrange(1, 511) )
    # Netem handles 
    ifb_up.nhandles = ( '{0:x}'.format(n) for n in xrange(512, 1023) )
    ifb_down.nhandles = ( '{0:x}'.format(n) for n in xrange(512, 1023) )
 
    def __setup(self):
        # root HTB qdiscs on IFB egress
        shapy.IFB.modprobe()
        self.ifb_up.add( shapy.HTBQdisc('1:', default_class='1ff') )
        self.ifb_down.add( shapy.HTBQdisc('1:', default_class='1ff') )
        
        # add ingress qdiscs to all real interfaces (such as eth or lo) so
        # we can redirect traffic to the IFB devices for the actual shaping
        for i in settings.EMU_INTERFACES:
            interface = shapy.Interface(i)
            prioq = shapy.PRIOQdisc('1:')
            ingressq = shapy.IngressQdisc()
            
            # Exclude specified ports from shaping altogether
            for port in settings.EMU_NOSHAPE_PORTS:
                prioq.add(shapy.FlowFilter('sport %s' % port, '1:1ff',
                                           mask=0xffff, prio=1))
                ingressq.add(shapy.FlowFilter('dport %s' % port, '1:1ff',
                                              mask=0xffff, prio=1))
            
            interface.add(prioq)    
            interface.add_ingress(ingressq) 
    
    
    def set_shaping(self, shaping_conf):
        """
        shaping_conf format:
        { (ip1, ...): {
            download: int [kbps/kbit],
            upload: int [kbps/kbit],
            delay: int [ms]}
            }
        }
        Each IP will have its own separate HTB class.
        """

        for node_ips in shaping_conf:
            # if the the user accidentally passes a string instead of one-item
            # list, we will do the conversion
            if isinstance(node_ips, str):
                node_ips = (str,)
            if not isinstance(node_ips, (list, tuple)):
                logger.warning("IPs must be specified in a list or tuple, skipping!")
                continue
            
            shaping_params = shaping_conf[node_ips]
            upload = shaping_params.get('upload', 2**32-1)
            download = shaping_params.get('download', 2**32-1)
            delay = shaping_params.get('delay', 0)
            jitter = shaping_params.get('jitter', 0)
            
            for ip in node_ips:
                utils.validate_ip(ip)
                
                if ip in self.ip_handles:
                    logger.info("{0} is already shaped, skipping.".format(ip))
                    continue
                logger.info("Configuring {0} -> U:{1}{units} D:{2}{units} delay:{3}ms jitter:±{4}ms"\
                            .format(ip, upload, download, delay, jitter, units=settings.UNITS))
                # upload shaping for the given set of IPs
                self.__shape_upload(ip, upload, delay, jitter)
                # download shaping
                self.__shape_download(ip, download, delay, jitter)
        
        # finally, we need to actually run those rules we just created
        for i in settings.EMU_INTERFACES:
            logger.info("Setting up shaping/emulation on interface {0}:".format(i))
            shapy.Interface(i).set_shaping()
        logger.info("Setting up IFB devices:")
        self.ifb_up.set_shaping()
        self.ifb_down.set_shaping()

    
    def teardown_all(self):
        """
        This method does not properly reset Shaper object for further use.
        It just purges external configuration. Use reset_all() if you intend
        to reuse this instance.
        """
        for i in settings.EMU_INTERFACES:
            logger.info("Tearing down %s" % i)
            shapy.Interface(i).teardown()
        logger.info("Tearing down IFBs")
        shapy.IFB.teardown()

    def reset_all(self):
        """
        Completely resets this instance and all associated rules in
        underlying OS so you can reuse this instance.
        """
        self.teardown_all()
        self.__setup()
    
    def get_traffic(self, ip):
        """
        Returns sent/received data for the given IP. This is based on
        tc statistics (tc -s) of HTB classes on the respective IFB devices.
        """
        if not hasattr(self, 'ip_handles'):
            return None, None
        
        def get_htb_class_send(stats):
            try:
                return int(re.search(r"Sent ([0-9]+) ", stats).group(1))
            except:
                return None, None
        
        handle = self.ip_handles[ip]
        up = executor.get_command('TCStats', interface=self.ifb_up, handle=handle)
        down = executor.get_command('TCStats', interface=self.ifb_down, handle=handle)
        up_stats = executor.run(up, sudo=False)
        down_stats = executor.run(down, sudo=False)
        
        return get_htb_class_send(up_stats), get_htb_class_send(down_stats)
    

    def __init__(self, **kwargs):
        # stores the relationship between IP and it's policing HTB classes
        self.ip_handles = {}
        self.__setup()

    
    def __shape_upload(self, ip, rate, delay, jitter):
        """Sets up upload shaping (not really policing) and emulation
        for the given _ip_."""
        # egress filter to redirect to IFB, upload -> src <ip> & ifb1
        for i in settings.EMU_INTERFACES:
            f = shapy.RedirectFilter('src %s' % ip, self.ifb_up)
            shapy.Interface(i).root.add(f)
        qh = self.ifb_up.qhandles.next()
        nh = self.ifb_up.nhandles.next()
        self.ip_handles.update({ip: qh})
        self.__shape_ifb(self.ifb_up, 'src %s' % ip, qh, rate, nh, delay, jitter)
    
    
    def __shape_download(self, ip, rate, delay, jitter):
        """Sets up download shaping and emulation for the given _ip_."""
        # ingress filter to redirect to IFB, download -> dst <ip> & ifb0
        for i in settings.EMU_INTERFACES:
            f = shapy.RedirectFilter('dst %s' % ip, self.ifb_down)
            shapy.Interface(i).ingress.add(f)
        qh = self.ifb_down.qhandles.next()
        nh = self.ifb_down.nhandles.next()
        self.__shape_ifb(self.ifb_down, 'dst %s' % ip, qh, rate, nh, delay, jitter)
    
    
    def __shape_ifb(self, ifb, ip, qhandle, rate, nhandle, delay, jitter):
        """Creates rules on IFB device itself."""
        # filter on the IFB device itself to redirect traffic to a HTB class
        ifb.root.add( shapy.FlowFilter(ip, '1:%s' % qhandle) )
        htbq = shapy.HTBClass('1:%s' % qhandle, rate=rate, ceil=rate)
        if delay or jitter:
            htbq.add(shapy.NetemDelayQdisc('%s:' % nhandle, delay, jitter))
        ifb.root.add( htbq )
