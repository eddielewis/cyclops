class Receive():
    def __init__(self, process_msg, socket, ip, port):
        self.process_msg = process_msg
        self.socket = socket
        self.socket.bind((ip, port))

    def listen():
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    process_msg(data)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False


