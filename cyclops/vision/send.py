class Send():
    def __init__(self, socket):
        self.socket = socket

    def send(msg, ip, port):
        socket.sendto(msg, (ip, port))


class ClientSend(Send):
    def __init__(self, server_ip, server_port):
        super(ClientSend, self).__init__(socket)
        self.server_ip = server_ip
        self.server_port = server_port

    def send(msg):
        socket.sendto(msg, self.server_ip, self.server_port)
