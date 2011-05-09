
HTBRootQdisc = """\
tc qdisc add dev {interface!s} root handle 1: \
htb default {default_class!s}\
"""

HTBQdisc = """\
tc qdisc add dev {interface!s} parent {parent!s} handle {handle!s} \
htb default {default_class!s}\
"""

NetemDelayQdisc = """\
tc qdisc add dev {interface!s} parent {parent!s} handle {handle!s} \
netem delay {delay!s}ms\
"""

IngressQdisc = "tc qdisc add dev {interface!s} ingress"

PRIOQdisc = "tc qdisc add dev {interface!s} root handle 1: prio"

pfifoQdisc = "tc qdisc add dev {interface!s} root handle 1: pfifo"