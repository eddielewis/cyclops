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
        self.netgear_server = NetGear(
            address=netgear.ip, port=netgear.port, protocol="tcp", pattern=2, **netgear.options.__dict__)
        self.stream = PiGear(
            resolution=(camera.width, camera.height),
            framerate=camera.framerate,
            logging=True, **camera.options.__dict__)
        self.stream.start()
        self.frame_count = 0

    def load_camera_matrix(self, sensor_mode):
        # The camera matrices are saved in the same directory on every Pi
        # They are differentiated using the sensor mode and the camera id
        path = "/home/pi/ce301_lewis_edward_f/cyclops/calibration/data/calibration_images_%s_%s/matrix_%s_%s.npz" % (
            self.camera_id[:-6], sensor_mode, self.camera_id[:-6], sensor_mode)
        # Loads the camera calibration results
        with np.load(path) as f:
            self.camera_matrix, self.dist_coefs, self.rvecs, self.tvecs = [f[i] for i in (
                'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]

    # Shuts the camera stream and netgear server down
    def close(self):
        self.stream.stop()
        self.netgear_server.close()

    # Takes an image and sends it to the client
    def snap(self):
        frame = self.stream.read()
        # Undistorts the image using the camera calibration matridx
        frame = cv2.undistort(frame, self.camera_matrix, self.dist_coefs)
        frame_data = {
            "camera_id": self.camera_id,
            "frame_count": self.frame_count
        }
        print(frame_data)
        # Converts frame data to JSON
        frame_data_json = json.dumps(frame_data)
        # Sends the frame and frame data to the client
        self.netgear_server.send(frame, message=frame_data_json)
        # Increments the frame counter
        self.frame_count += 1
