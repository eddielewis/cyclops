from vidgear.gears import PiGear
from vidgear.gears import NetGear
import json
import cv2
import socket
import numpy as np


class CameraServer:
    def __init__(self, camera, netgear):
        self.camera_id = socket.gethostname() + ".local"
        self.load_camera_matrix(camera.sensor_mode)

        options = netgear.options
        self.netgear_server = NetGear(
            address=netgear.ip, port=netgear.port, protocol="tcp", pattern=2, **netgear.options.__dict__
        )

        self.stream = PiGear(
            resolution=(camera.width, camera.height),
            framerate=camera.framerate,
            logging=True, **camera.options.__dict__)
        self.stream.start()

        self.frame_count = 0

    def load_camera_matrix(self, sensor_mode):
        path = "/home/pi/ce301_lewis_edward_f/cyclops/calibration/data/calibration_images_%s_%s/matrix_%s_%s.npz" % (
            self.camera_id[:-6], sensor_mode, self.camera_id[:-6], sensor_mode)

        with np.load(path) as f:
            self.camera_matrix, self.dist_coefs, self.rvecs, self.tvecs = [f[i] for i in (
                'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]
            print(self.camera_matrix)

    def close(self):
        self.stream.stop()
        self.netgear_server.close()

    def snap(self):
        frame = self.stream.read()
        frame = cv2.undistort(frame, self.camera_matrix, self.dist_coefs)
        frame_data = {
            "camera_id": self.camera_id,
            "frame_count": self.frame_count
        }
        print(frame_data)
        frame_data_json = json.dumps(frame_data)
        self.netgear_server.send(frame, message=frame_data_json)
        self.frame_count += 1
