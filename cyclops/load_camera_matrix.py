import numpy as np
import sys
import argparse
import socket
import os

CAMERA_ID = socket.gethostname()
SENSOR_MODE = 7

# sys.path = "/home/pi/ce301_lewis_edward_f/cyclops/"
# print(sys.path)

with np.load(os.environ.get("CYCLOPS_PATH") + "calibration/data/calibration_images_%s_%s/matrix_%s_%s.npz" % (CAMERA_ID, SENSOR_MODE, CAMERA_ID, SENSOR_MODE)) as f:
    camera_matrix, dist_coefs, rvecs, tvecs = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]
