import cv2
import threading
import socketserver
import socket
from numpy import true_divide
from vidgear.gears import PiGear
from vidgear.gears import NetGear
import json

commands = [
    b"start_capture",
    b"stop_capture",
    b"snap",
    b"preview",
    b"stop_preview"
]


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        try:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            # just send back the same data, but upper-cased
            if self.data in commands:
                if self.data == b"snap":
                    snap()
                elif self.data == b"preview":
                    t = threading.Thread(target=preview())
                    t.start()
                elif self.data == b"stop_preview":
                    stop_preview()
        except KeyboardInterrupt:
            server.shutdown()
            server.socket.close()
            stream.stop()
            server_netgear.close()


def start_capture():
    global stream
    global frame_count
    options = {
        "hflip": False,
        "exposure_mode": "auto",
        "iso": 800,
        "exposure_compensation": 15,
        "awb_mode": "horizon",
        "sensor_mode": 0,
    }
    stream = PiGear(resolution=(1920, 1080), framerate=30,
                    logging=True, **options)
    stream.start()
    frame_count = 0


def stop_capture():
    stream.close()


def snap():
    global frame_count
    frame = stream.read()
    cv2.imwrite("frame.png", frame)
    frame_data = {
        "camera_id": camera_id,
        "frame_count": frame_count
    }
    frame_data_json = json.dumps(frame_data)
    # send frame and frame data to client
    server_netgear.send(frame, message=frame_data_json)
    print(frame_count)
    frame_count += 1


def preview():
    global preview
    while preview:
        global frame_count
        frame = stream.read()
        cv2.imwrite("frame.png", frame)
        frame_data = {
            "camera_id": camera_id,
            "frame_count": frame_count
        }
        frame_data_json = json.dumps(frame_data)
        # send frame and frame data to client
        server_netgear.send(frame, message=frame_data_json)
        print(frame_count)
        frame_count += 1


def stop_preview():
    global preview
    preview = False


options = {"multiserver_mode": True}

machine_ip = socket.gethostbyname("barold.local")
server_netgear = NetGear(
    address=machine_ip, port="5566", protocol="tcp", pattern=2, **options
)

camera_id = socket.gethostname()


start_capture()


HOST = "0.0.0.0"
PORT = 5005

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.socket.close()
        stream.stop()
        server_netgear.close()
