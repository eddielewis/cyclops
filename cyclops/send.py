import socket
import json

PORT = 5005
# PI_HOSTNAMES = ["cyclops0.local", "cyclops1.local"]
PI_HOSTNAMES = ["cyclops0.local"]


ip_addresses = []

obj = {"command": "close"}
message = json.dumps(obj)
message = message.encode("utf-8")

for hostname in PI_HOSTNAMES:
    ip = socket.gethostbyname(hostname)
    ip_addresses.append(ip)

for ip in ip_addresses:
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP

    sock.sendto(message, (ip, PORT))
