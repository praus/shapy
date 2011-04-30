import os, sys
import re
import subprocess
import shlex
import logging
import logging.handlers
#from string import Template

logger = logging.getLogger('shapy.executor')

from shapy import settings
from shapy.exceptions import ImproperlyConfigured

def run(command, **kwargs):
    command = shlex.split(command)
    if kwargs.pop('sudo', True):
        #command.insert(0, '-S')
        command.insert(0, 'sudo')
        
    #logger.info(">> %s" % ' '.join(command)); return
    
    p = subprocess.Popen(command, bufsize=-1, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=settings.ENV)
    
    #if hasattr(settings, 'SUDO_PASSWORD'):
    #    p.stdin.write('%s\n' % settings.SUDO_PASSWORD)
    stdout, stderr = p.communicate()
    
    if p.returncode == 0:
        logger.info('[{1}] {0}'.format(' '.join(command), p.returncode))
    else:
        fmt = """[{1}] {0} [{2}]"""
        logger.error(fmt.format(' '.join(command), p.returncode, stderr.strip()))
        
    return stdout


def get_command(name, **kwargs):
    try:
        __import__(settings.COMMANDS)
        cmd = getattr(sys.modules[settings.COMMANDS], name)
        if kwargs:
            cmd = cmd.format(**kwargs)
        return cmd
    except AttributeError:
        msg = "Command '%s' undefined!" % name
        logger.critical(msg)
        raise ImproperlyConfigured(msg)
    except KeyError, ImportError:
        msg = "Missing commands module (%s)!" % settings.COMMANDS
        logger.critical(msg)
        raise ImproperlyConfigured(msg)


class Executable(object):
    def __init__(self, **kwargs):
        self.opts = kwargs
        self.executed = False
    
    def __setitem__(self, key, item):
        self.opts.update({key: item})
    
    def __getitem__(self, key):
        return self.opts[key]
    
    @property
    def cmd(self):
        return get_command(self.__class__.__name__)

    def get(self):
        self.opts.update(self.get_context())
        return self.cmd.format(**self.opts)
    
    def get_context(self):
        has_p = getattr(self, 'parent', None)
        return {'parent': self.parent['handle'] if has_p else '',
                'interface': self.get_interface()}
    
    def get_interface(self):
        p = getattr(self, 'parent', self)
        while hasattr(p, 'parent'):
            p = getattr(p, 'parent')
        try:
            return getattr(p, 'interface')
        except AttributeError:
            msg = "Element {0!r} has no interface".format(self)
            logger.critical(msg)
            raise ImproperlyConfigured(msg)
        
    def execute(self):
        if not self.executed:
            run(self.get())
        else:
            logger.debug("Command %s was already executed."% self.get())
        