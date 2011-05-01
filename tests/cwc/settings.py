
COMMANDS = 'cwc.commands'

### CWC settings ###

# it's advisable to set MTU of the interfaces to something real, for example 1500
CWC_INTERFACES = (
    'lo',
)

# ports excluded from shaping and delaying (holds for in and out)
# usually used for control ports
CWC_NOSHAPE_PORTS = (8000,)
