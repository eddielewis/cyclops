import time
import socket

from ssh2.session import Session

PASSWORD = "corsairk100"
PI_HOSTNAMES = ["cyclops0.local", "cyclops1.local"]
USER = "pi"

ENV = "source /home/pi/.virtualenvs/cv/bin/activate &&"
PROJECT_ROOT = "/home/pi/ce301_lewis_edward_f/cyclops"


""" host = socket.gethostbyname(PI_HOSTNAMES[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 22))

session = Session()
session.handshake(sock)
# session.agent_auth(user)
session.userauth_password(
    USER, PASSWORD)

channel = session.open_session()
# channel.execute('echo me; exit 2')
channel.execute("%s %s/run_server.sh" % (ENV, PROJECT_ROOT))
size, data = channel.read()
while size > 0:
    print(data)
    size, data = channel.read()
channel.close()
print("Exit status: %s" % channel.get_exit_status()) """


channels = {}


def setup(hostname):
    host_ip = socket.gethostbyname(hostname)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host_ip, 22))

    session = Session()
    session.handshake(sock)
    session.userauth_password(
        USER, PASSWORD)

    return session.open_session()


def run_server(hostname):
    channel = setup(hostname)
    channel.execute("%s %s/run_server.sh" % (ENV, PROJECT_ROOT))
    channel.close()


def kill_server(hostname):
    print("iouesfkhbnsef")
    channel = setup(hostname)
    channel.execute("pkill python")
    print("iouesfkhbnsef")
    size, data = channel.read()
    print(data)
    channel.close()


run_server("cyclops0.local")
time.sleep(2.0)
kill_server("cyclops0.local")
