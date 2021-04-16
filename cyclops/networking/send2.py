import socket
import json

PORT = 5005
# PI_HOSTNAMES = ["cyclops0.local", "cyclops1.local"]
PI_HOSTNAMES = ["barry.local"]


ip_addresses = []

obj = {"command": "save_snap"}
message = json.dumps(obj)
message = message.encode("utf-8")

for hostname in PI_HOSTNAMES:
    ip = socket.gethostbyname(hostname)
    ip_addresses.append(ip)

for ip in ip_addresses:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, PORT))
    sock.sendto(message, (ip, PORT))
