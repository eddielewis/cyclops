from stitch import estimate_homography, matrix_id
import argparse
import json
from vidgear.gears import NetGear
import cv2
import socket
import numpy as np

# activate multiserver_mode
options = {"multiserver_mode": True}

# Define NetGear Client at given IP address and assign list/tuple
# of all unique Server((5566,5567) in our case) and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
client = NetGear(
    address=ip,
    port=(5566, 5567),
    protocol="tcp",
    pattern=2,
    receive_mode=True,
    **options
)

frame_dict = {}

camera_layout = ["cyclops0", "cyclops1"]
while True:
    try:
        # receive data from network
        data = client.recv()

        # check if data received isn't None
        if data is None:
            break

        # extract unique port address and its respective frame
        unique_address, extracted_data, frame = data

        data = json.loads(extracted_data)
        camera_id = data["camera_id"]
        print(camera_id)
        frame_dict[camera_id] = frame

        if len(frame_dict) == len(camera_layout):
            break
    except KeyboardInterrupt:
        break

h_matrices = {}

for i in range(len(camera_layout)-1):
    cam_a_id = camera_layout[i]
    cam_b_id = camera_layout[i+1]

    imgs = [frame_dict[cam_a_id], frame_dict[cam_b_id]]
    H = estimate_homography(imgs)
    m_id = matrix_id(cam_a_id, cam_b_id)
    h_matrices[m_id] = H
print(h_matrices)
np.savez('h_matrices.npz', h_matrices=h_matrices, camera_layout=camera_layout)
print("Saved matrices")

client.close()
