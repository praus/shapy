#!/usr/bin/env python

from distutils.core import setup
import os
import sys

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '': 
    os.chdir(root_dir)
project_dir = 'shapy'

for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(name='ShaPy',
      version='1.0',
      description='Netlink and network emulation framework',
      author='Petr Praus',
      author_email='petr@praus.net',
      url='https://github.com/praus/shapy',
      packages=packages,
      #packages=['shapy', 'shapy.emulation', 'shapy.emulation.commands',
      #          'shapy.framework', 'shapy.framework.netlink'],
     )
