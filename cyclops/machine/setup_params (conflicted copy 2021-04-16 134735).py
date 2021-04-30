from position import find_markers
from imutils import build_montages
import time
import cv2
import argparse
import numpy as np
from zmq.sugar import frame
import cv2.aruco as aruco
from position import calc_m_per_px
from stitch import estimate_homography, matrix_id, Stitcher
import argparse
import json
from vidgear.gears import NetGear
import socket
import numpy as np

CAMERA_LAYOUT = ["cyclops0.local", "cyclops1.local"]


def calc_h_matrices(frame_dict):
    h_matrices = {}

    for i in range(len(CAMERA_LAYOUT)-1):
        cam_a_id = CAMERA_LAYOUT[i]
        cam_b_id = CAMERA_LAYOUT[i+1]

        imgs = [frame_dict[cam_a_id], frame_dict[cam_b_id]]
        H = estimate_homography(imgs)
        m_id = matrix_id(cam_a_id, cam_b_id)
        h_matrices[m_id] = H
    return h_matrices


def get_frames():
    options = {"multiserver_mode": True}
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
    while True:
        try:
            data = client.recv()
            if data is None:
                continue
            port, extracted_data, frame = data
            data = json.loads(extracted_data)
            camera_id = data["camera_id"]
            print(camera_id)
            frame_dict[camera_id] = frame

            (h, w) = frame.shape[:2]
            montages = build_montages(frame_dict.values(), (w, h), (2, 1))
            for (i, montage) in enumerate(montages):
                cv2.imshow("Montage Footage {}".format(i), montage)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        except KeyboardInterrupt:
            print("keyboard")
            break
    client.close()
    return frame_dict


parser = argparse.ArgumentParser()
parser.add_argument("output_fn",
                    type=str,
                    help="Filename for the parameters output (excluding extension)")
args = parser.parse_args()

frame_dict = get_frames()
for key, frame in frame_dict.items():
    cv2.imwrite(key + ".png", frame)
h_matrices = calc_h_matrices(frame_dict)
stitcher = Stitcher()
stitcher.set_params(h_matrices, CAMERA_LAYOUT)
stitched_img = stitcher.stitch_h(frame_dict, True)
cv2.imshow("stitched", stitched_img)
cv2.waitKey(0)
ids, corners = find_markers(stitched_img)
origin = np.array([0, 0, 0])
m_per_px = calc_m_per_px(corners, 0.025)


np.savez(args.output_fn+".npz", h_matrices=h_matrices,
         camera_layout=CAMERA_LAYOUT, origin=origin, m_per_px=m_per_px)
print("Saved matrices")
