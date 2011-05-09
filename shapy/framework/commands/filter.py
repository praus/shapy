
RedirectFilter = """\
tc filter add dev {interface!s} parent {parent!s} \
protocol ip prio {prio} u32 \
match ip {ip_match} flowid 1:1 \
action mirred egress redirect dev {ifb!s}\
"""

FlowFilter = """\
tc filter add dev {interface} parent {parent!s} \
protocol ip prio {prio} u32 \
match ip {ip_match} flowid {flowid}\
"""