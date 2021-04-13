from vidgear.gears import PiGear
from vidgear.gears import NetGear
import json
import cv2
from load_camera_matrix import camera_matrix, dist_coefs
import socket
import zmq


class CameraServer:
    def __init__(self):
        self.camera_id = socket.gethostname()
        options = {"multiserver_mode": True}
        machine_ip = socket.gethostbyname("barold.local")

        self.netgear_server = NetGear(
            address=machine_ip, port="5567", protocol="tcp", pattern=2, **options
        )

        options = {
            "hflip": False,
            "exposure_mode": "auto",
            "iso": 800,
            "exposure_compensation": 15,
            "awb_mode": "horizon",
            "sensor_mode": 0,
        }
        self.stream = PiGear(resolution=(1920, 1080), framerate=30,
                             logging=True, **options)
        self.stream.start()

        self.frame_count = 0

    def close(self):
        self.stream.stop()
        self.netgear_server.close()

    def snap(self):
        frame = self.stream.read()
        # frame = cv2.undistort(frame, camera_matrix, dist_coefs)
        frame_data = {
            "camera_id": self.camera_id,
            "frame_count": self.frame_count
        }
        frame_data_json = json.dumps(frame_data)
        self.netgear_server.send(frame, message=frame_data_json)
        self.frame_count += 1
