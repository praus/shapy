
HTBClass = """\
tc class add dev {interface} parent {parent} classid {handle} \
htb rate {rate}{units} ceil {ceil}{units}\
"""
