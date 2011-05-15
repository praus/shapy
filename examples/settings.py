def scan_interfaces():
    """Parses a list of all interfaces reported by `ip link`"""
    import subprocess
    import re
    ifcs = []
    out = subprocess.check_output(["ip", "link"]).split('\n')
    for line in out:
        m = re.match("^[0-9]+:[ ]([a-z0-9]+):", line)
        if m:
            ifcs.append(m.group(1))
    return ifcs

EMU_INTERFACES = scan_interfaces()
EMU_NOSHAPE_PORTS = ('8000',)

