import socketserver
import socket

import socket

# taken from w3resource.com
IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
HOSTNAME = socket.gethostname()
PORT = 5005

print(IP)

ip_addresses = []

PI_COUNT = 2

for i in range(PI_COUNT):
    hostname = "cyclops%s.local" % i
    if hostname != HOSTNAME + ".local":
        ip = socket.gethostbyname(hostname)
        print(ip)
        ip_addresses.append(ip)


class CyclopsServer(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(self.client_address)
        print(data)
        for ip in ip_addresses:
            socket.sendto(data.upper(), (ip, port))


if __name__ == "__main__":
    with socketserver.UDPServer((HOSTNAME, PORT), CyclopsServer) as server:
        server.serve_forever()
