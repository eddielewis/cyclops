import argparse
import json
from stitch import Stitcher
from vidgear.gears import NetGear
import multiprocessing as mp
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


frames = {}

# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--H",
                    help="Path to saved homography matrices",
                    type=str)
args = parser.parse_args()

if args.H:
    with np.load(args.H, allow_pickle=True) as f:
        h_matrices = f["h_matrices"]
        camera_layout = f["camera_layout"]
    stitcher = Stitcher()
    stitcher.load_matrices(args.H)
count = 0

# loop over until Keyboard Interrupted
while True:

    try:
        # receive data from network
        data = client.recv()

        # check if data received isn't None
        if data is None:
            break

        """ # extract unique port address and its respective frame
        unique_address, extracted_data, frame = data

        data = json.loads(extracted_data)
        camera_id, frame_count = data["camera_id"], int(data["frame_count"])
        if frames.get(frame_count) is None:
            frames[frame_count] = {
                camera_id: frame
            }
        else:
            frames[frame_count][camera_id] = frame

        if len(frames[count]) == len(camera_layout):
            img = stitcher.stitch(frames[count])
            cv2.imwrite("img.png", img)

            # check for 'q' key if pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break """

    except KeyboardInterrupt:
        break

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()
