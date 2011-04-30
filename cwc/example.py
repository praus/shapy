import logging
logging.basicConfig(level=logging.INFO, datefmt='%H:%M:%S',
                    format='%(asctime)s %(levelname)s: %(message)s')

from shapy import register_settings
register_settings('settings')
from cwc.shaper import Shaper

if __name__ == '__main__':
    ps = {("127.0.0.2",) : {'upload': 256, 'download': 1024, 'delay': 5},
          ("127.0.0.3",) : {'upload': 256, 'download': 256, 'delay': 30},
          }

    sh = Shaper()
    sh.set_shaping(ps)

    #print sh.ip_handles
    
    #import pdb; pdb.set_trace()
    import time
    time.sleep(1)
    
    #sh.teardown_all()
    
    #up, down = sh.get_traffic("127.0.0.2")
    #print up, down
    
    
    # Please be aware that second call to set_shaping with the same IP will not change the settings

    # How to generate large range of IP adresses:    
    #ps = {tuple([ "127.0.0.%d" % x for x in range(1,250) ]) : {'upload': 256, 'download': 1024, 'delay': 25},
    #      }
#    
#    sh.set_shaping(ps)
    
    # Reuse of the same instance:
#    sh.reset_all()
#    
#    ps = {("127.0.0.2",) : {'upload': 512, 'download': 512, 'delay': 5},
#          }
#    sh.set_shaping(ps)

