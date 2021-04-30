import socketserver

# The list of commands the server will recognise
commands = [
    b"stop",
    b"snap"
]


class PiTCPServer(socketserver.TCPServer):
    def __init__(self, camera_server, *args, **kwargs):
        self.camera_server = camera_server
        super(PiTCPServer, self).__init__(*args, **kwargs)

    # Overrides the RequestHandler to pass the CameraServer object, allowing the server to call snap() to take an image
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

    # Method is called to handle the request
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # Only recognises commands defined at the top of the script
        if self.data in commands:
            if self.data == b"snap":
                self.camera_server.snap()
        else:
            # Generates error message
            error_message = b"Command \"" + self.data + b"\" not recognised"
            # Returns error to client
            self.request.sendall(error_message)
            # Prints error
            print(error_message)

    # Closes the server properly
    def server_close(self):
        self.socket.close()
