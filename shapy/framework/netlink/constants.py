TC_H_UNSPEC     = 0
TC_H_ROOT       = 0xFFFFFFFF
TC_H_INGRESS    = 0xFFFFFFF1

# flags
NLM_F_REQUEST   = 1 
NLM_F_MULTI     = 2 
NLM_F_ACK       = 4 
NLM_F_ECHO      = 8

# Modifiers (flags) to GET requests
NLM_F_ROOT      = 0x100
NLM_F_MATCH     = 0x200
NLM_F_ATOMIC    = 0x400
NLM_F_DUMP      = NLM_F_ROOT | NLM_F_MATCH

# Modifiers to NEW request
NLM_F_REPLACE   = 0x100   # Override existing
NLM_F_EXCL      = 0x200   # Do not touch, if it exists
NLM_F_CREATE    = 0x400   # Create, if it does not exist
NLM_F_APPEND    = 0x800   # Add to end of list


###################
## Message types ##
###################

NLMSG_NOOP  = 1 
NLMSG_ERROR = 2 
NLMSG_DONE  = 3 
NLMSG_OVERRUN   = 4 
NLMSG_MIN_TYPE  = 0x10

RTM_BASE        = 16

RTM_NEWLINK	= 16
RTM_DELLINK     = 17
RTM_GETLINK     = 18
RTM_SETLINK     = 19

RTM_NEWADDR	= 20
RTM_DELADDR     = 21
RTM_GETADDR     = 22

RTM_NEWROUTE    = 24
RTM_DELROUTE    = 25
RTM_GETROUTE    = 26

RTM_NEWNEIGH    = 28
RTM_DELNEIGH    = 29
RTM_GETNEIGH    = 30

RTM_NEWRULE	= 32
RTM_DELRULE     = 33
RTM_GETRULE     = 34

RTM_NEWQDISC	= 36
RTM_DELQDISC    = 37
RTM_GETQDISC    = 38

RTM_NEWTCLASS	= 40
RTM_DELTCLASS   = 41
RTM_GETTCLASS   = 42
	
RTM_NEWTFILTER	= 44
RTM_DELTFILTER  = 45
RTM_GETTFILTER  = 46

RT_TABLE_MAIN   = 254


IFLA_MTU = 4

### Traffic Control (Qdisc) ###
TCA_UNSPEC  = 0
TCA_KIND    = 1
TCA_OPTIONS = 2
TCA_STATS   = 3
TCA_XSTATS  = 4
TCA_RATE    = 5
TCA_FCNT    = 6
TCA_STATS2  = 7
TCA_STAB    = 8


### HTB Class ###
TCA_HTB_UNSPEC  = 0
TCA_HTB_PARMS   = 1
TCA_HTB_INIT    = 2
TCA_HTB_CTAB    = 3
TCA_HTB_RTAB    = 4


### Filter attributes ###
TCA_U32_UNSPEC  = 0
TCA_U32_CLASSID = 1
TCA_U32_HASH    = 2
TCA_U32_LINK    = 3
TCA_U32_DIVISOR = 4
TCA_U32_SEL     = 5
TCA_U32_POLICE  = 6
TCA_U32_ACT     = 7
TCA_U32_INDEV   = 8
TCA_U32_PCNT    = 9
TCA_U32_MARK    = 10

# U32 filter flags
TC_U32_TERMINAL  = 1
TC_U32_OFFSET    = 2
TC_U32_VAROFFSET = 4
TC_U32_EAT       = 8
TC_U32_MAXDEPTH  = 8

# Filter actions
TCA_ACT_MIRRED      = 8
TCA_EGRESS_REDIR    = 1  # packet redirect to EGRESS
TCA_EGRESS_MIRROR   = 2  # mirror packet to EGRESS
TCA_INGRESS_REDIR   = 3  # packet redirect to INGRESS
TCA_INGRESS_MIRROR  = 4  # mirror packet to INGRESS

TCA_ACT_UNSPEC   = 0
TCA_ACT_KIND     = 1
TCA_ACT_OPTIONS  = 2
TCA_ACT_INDEX    = 3
TCA_ACT_STATS    = 4

# filter action flags
TC_ACT_UNSPEC       = -1
TC_ACT_OK           = 0
TC_ACT_RECLASSIFY   = 1
TC_ACT_SHOT         = 2
TC_ACT_PIPE         = 3
TC_ACT_STOLEN       = 4
TC_ACT_QUEUED       = 5
TC_ACT_REPEAT       = 6
TC_ACT_JUMP         = 0x10000000

# mirred params
TCA_MIRRED_UNSPEC = 0
TCA_MIRRED_TM     = 1
TCA_MIRRED_PARMS  = 2



### Kernel Ethernet protocol numbers
# see include/linux/if_ether.h
ETH_P_IP = 0x08

#enum {
#	RTM_NEWACTION	= 48,
#	RTM_DELACTION,
#	RTM_GETACTION,

#	RTM_NEWPREFIX	= 52,

#	RTM_GETMULTICAST = 58,

#	RTM_GETANYCAST	= 62,

#	RTM_NEWNEIGHTBL	= 64,
#	RTM_GETNEIGHTBL	= 66,
#	RTM_SETNEIGHTBL,

#	RTM_NEWNDUSEROPT = 68,

#	RTM_NEWADDRLABEL = 72,
#	RTM_DELADDRLABEL,
#	RTM_GETADDRLABEL,

#	RTM_GETDCB = 78,
#	RTM_SETDCB,
#};