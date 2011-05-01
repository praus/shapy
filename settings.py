
COMMANDS = 'cwc.commands'

### CWC settings ###

# it is advisable to set MTU of the interfaces to something
# real, for example 1500 bytes
CWC_INTERFACES = (
    'lo',
    'eth0',
)

# ports excluded from shaping and delaying (holds for in and out)
# usually used for control ports
CWC_NOSHAPE_PORTS = (8000,)

with open('sudo_password.txt', 'r') as f:
    SUDO_PASSWORD = f.readlines()[0].strip()
