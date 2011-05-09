from shapy.framework.executor import Executable

class Filter(Executable):
    children = [] # filter cannot have children

class U32Filter(Filter):
    """Abstract filter for matching IP address."""
    def __init__(self, ip_match, **kwargs):
        Filter.__init__(self, **kwargs)
        self.opts.update({'ip_match': ip_match})

class RedirectFilter(U32Filter):
    """Redirecting traffic to (mainly) IFB devices"""
    def __init__(self, ip_match, ifb, **kwargs):
        U32Filter.__init__(self, ip_match, **kwargs)
        self.opts.update({'ifb': ifb,
                          'prio': kwargs.get('prio', '2')})

class FlowFilter(U32Filter):
    """Classifying traffic to classes."""
    def __init__(self, ip_match, flowid, **kwargs):
        U32Filter.__init__(self, ip_match, **kwargs)
        self.opts.update({'flowid': flowid,
                          'prio': kwargs.get('prio', '3')})