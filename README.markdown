## Introduction

ShaPy can be used to easily create an emulated network. ShaPy consists from two
main parts: ShaPy Framework and ShaPy Emulation. ShaPy Framework allows
accessing traffic control capabilities of the Linux kernel using the Netlink
interface. ShaPy Emulation builds on the framework and focuses on building
emulated network.

## Examples

### ShaPy Emulation

The following snippet gives you a virtual network of three IP addresses with
exactly the declared speeds and delays.

```python
from shapy.emulation.shaper import Shaper

ps = {("127.0.0.2",) : {'upload': 1024, 'download': 1024, 'delay': 56},
      ("127.0.0.3",) : {'upload': 256, 'download': 512, 'delay': 30},
      ("127.0.0.4",) : {'upload': 256, 'download': 512, 'delay': 30},
}

sh = Shaper()
sh.set_shaping(ps)
```

### ShaPy Framework
The following snippet is an example of ShaPy Framework. It creates a HTB qdisc
as a root qdisc on interface `lo`, creates a HTB class with maximum throughput
500 kbit (units are set in settings, see below) and a filter that will redirect
all traffic with source IP 127.0.0.3 to the HTB class to be shaped.

```python
lo = Interface('lo')
h1 = HTBQdisc('1:', default_class='1ff')
h1.add( FlowFilter('src 127.0.0.3', '1:1', prio=2) )
h1.add( HTBClass('1:1', rate=500, ceil=500) )
lo.add( h1 )
lo.set_shaping()
```

### ShaPy Settings
Shapy framework provides a simple facility for managing settings. User creates a
regular Python file accessible as a module. In his main program he subsequently
registers this module as shown below. The module name is not important but the
convention is to call it `settings.py`. The custom settings file can override or
add values specified in the default ShaPy settings module
`shapy.framework.settings.default`.


```python
import shapy
shapy.register_settings('settings')
```

Settings file for ShaPy Emulation might look like this:

```python
COMMANDS = 'shapy.emulation.commands'
UNITS = 'kbit'

### CWC settings ###

# it's advisable to set MTU of the interfaces to something real, for example 1500
CWC_INTERFACES = (
    'lo',
)

# ports excluded from shaping and delaying (holds for in and out)
# usually used for control ports
CWC_NOSHAPE_PORTS = (8000,)

```