import subprocess
import shlex

class PingError(OSError):
    pass

def ping(host_from, host_to, count=4, interval=0.2):
    """
    ICMP packets has to be sent by a process owned by the root, /bin/ping has
    setuid so I'm using this to avoid juggling with root privileges.
    This is blocking.
    """
    assert interval>=0.2, "Interval cannot be less than 0.2 seconds"
    cmd = 'ping -c {count} -I {0} -i {interval} {1}'\
                    .format(host_from, host_to, interval=interval, count=count)
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
        return float(stdout.splitlines()[-1].split('/')[4])
    raise PingError(p.returncode)


def eta(filesize, a, b):
        """
        Determines how long the transfer of filesize bytes from A to B should take.
        units for filesize are bytes, a and b is speed in kilobytes
        """
        return filesize/(min(a, b)*1024)

def total_seconds(td):
    """
    http://docs.python.org/library/datetime.html#datetime.timedelta.total_seconds
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / float(10**6)
    

def random_file(size):
    with open('/dev/urandom', 'rb') as f:
        return bytearray(f.read(size))
    
