from imutils import build_montages
import cv2
import argparse
import numpy as np
from stitch import calc_t_matrices, Stitcher
import argparse
import json
from vidgear.gears import NetGear
import socket
import numpy as np

# Constant that specifies the order of the cameras
CAMERA_LAYOUT = ["cyclops0.local", "cyclops1.local"]


def get_frames():
    options = {"multiserver_mode": True}
    # Resolves this computer's IP
    # Taken from w3resources.com
    ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
        ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    # Starts NetGear client to receive frames from the Pis
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
            # Waits on the next message received
            data = client.recv()
            if data is None:
                continue
            # Extract the data from the message
            port, extracted_data, frame = data
            data = json.loads(extracted_data)
            camera_id = data["camera_id"]
            # Add the frame to the dict, if the dict doesn't exist, create it
            frame_dict[camera_id] = frame
            # Create a montage of the frames recieved from each Pi
            (h, w) = frame.shape[:2]
            montages = build_montages(frame_dict.values(), (w, h), (2, 1))
            for (i, montage) in enumerate(montages):
                cv2.imshow("Montage Footage {}".format(i), montage)
            # Exits the function when q is pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        except KeyboardInterrupt:
            break
    # Shuts down the NetGear client
    client.close()
    return frame_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_fn",
                        type=str,
                        help="Filename for the parameters output (excluding extension)")
    args = parser.parse_args()

    frame_dict = get_frames()
    t_matrices = calc_t_matrices(frame_dict)

    stitcher = Stitcher()
    stitcher.set_params(t_matrices, CAMERA_LAYOUT)
    stitched_img = stitcher.stitch_h(frame_dict)

    np.savez(args.output_fn+".npz", t_matrices=t_matrices,
             camera_layout=CAMERA_LAYOUT)
    print("Saved matrices")

    cv2.imwrite("stitched_image.png", stitched_img)
    cv2.imshow("Stitched Image", stitched_img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
