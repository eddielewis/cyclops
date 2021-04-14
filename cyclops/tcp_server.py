import socketserver
import socket
# from camera import CameraServer

commands = [
    b"stop",
    b"snap"
]


class PiTCPServer(socketserver.TCPServer):
    def __init__(self, camera_server, *args, **kwargs):
        self.camera_server = camera_server
        super(PiTCPServer, self).__init__(*args, **kwargs)

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(
            self.camera_server, request, client_address, self)


class PiTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, camera_server, *args, **kwargs):
        self.camera_server = camera_server
        super(PiTCPHandler, self).__init__(*args, **kwargs)

    def handle(self):
        self.data = self.request.recv(1024).strip()
        if self.data in commands:
            if self.data == b"snap":
                self.camera_server.snap()
                # self.request.sendall(self.data.upper())
        else:
            error_message = b"Command \"" + self.data + b"\" not recognised"
            self.request.sendall(error_message)
            print(error_message)

    def server_close(self):
        self.socket.close()
