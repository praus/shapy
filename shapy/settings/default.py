try:
    with open('sudo_password.txt', 'r') as f:
        SUDO_PASSWORD = f.readlines()[0].strip()
except IOError:
    SUDO_PASSWORD = ''

# units can be either kbit meaning kilobits or kbps meaning kilobytes
UNITS = 'kbps'

ENV = {
    'PATH': '/sbin:/bin:/usr/bin'
}

COMMANDS = 'shapy.commands'

HTB_DEFAULT_CLASS = '1ff'
