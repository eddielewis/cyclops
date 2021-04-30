#!/home/pi/.virtualenvs/cv/bin/python
from camera import CameraServer
from gpio import GPIOHandler
from tcp_server import PiTCPServer, PiTCPHandler
import threading
import json
from types import SimpleNamespace
import socket
import argparse


class App():
    def __init__(self, fn):
        # Loads config.json to pass parameters to objects
        with open('config.json') as f:
            data = f.read().replace('\n', '')
            config = json.loads(
                data, object_hook=lambda d: SimpleNamespace(**d))
        config.netgear.ip = socket.gethostbyname(config.s_hostname)

        # Starts the camera server and the netgear server
        self.camera_server = CameraServer(
            config.camera, config.netgear)
        # Sets up the GPIO event listeners
        self.gpio = GPIOHandler(config.gpio, self.camera_server)

        # Instantiates the TCP to listen for commands
        PiTCPServer.allow_reuse_address = True
        self.tcp_server = PiTCPServer(
            self.camera_server, (config.tcp.host, config.tcp.port), PiTCPHandler)

    def run(self, preview):
        if preview:
            # Ignores TCP server and instead constantly streams frames to the client
            while True:
                try:
                    self.camera_server.snap()
                except KeyboardInterrupt:
                    print("Exiting")
                    break
        else:
            # Listens for TCP messages on the main thread
            while True:
                try:
                    self.tcp_server.serve_forever()
                except KeyboardInterrupt:
                    print("Exiting")
                    break
            # Creates a new thread to shutdown
            # This must be done to prevent deadlock according to the docs
            t = threading.Thread(target=self.tcp_server.shutdown())
            t.start()
            t.join()

        # Calls the shutdown methods for the other objects
        self.gpio.close()
        self.camera_server.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fn", type=str, help="Filename for the config file")
    # Boolean flag for preview that defaults to false
    parser.add_argument("--preview", nargs="?",
                        type=bool,
                        default=False, const=True)
    args = parser.parse_args()
    app = App(args.fn)
    app.run(args.preview)


if __name__ == "__main__":
    main()
