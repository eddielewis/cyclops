import socket


PORT = 5005
PI_COUNT = 1

ip_addresses = []

for i in range(PI_COUNT):
    hostname = "cyclops%s.local" % i
    ip = socket.gethostbyname(hostname)
    ip_addresses.append(ip)

for ip in ip_addresses:
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(b"snap", (ip, PORT))
