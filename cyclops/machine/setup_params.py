from imutils import build_montages
import cv2
import cv2.aruco as aruco
import argparse
import numpy as np
from stitch import calc_t_matrices, Stitcher
import argparse
import json
from vidgear.gears import NetGear
import socket
import numpy as np

from stitch import PX_DIST

# Constant that specifies the order of the cameras
CAMERA_LAYOUT = ["cyclops1.local", "cyclops0.local"]


def calc_t_matrices(frame_dict):
    t_matrices = {}

    for i in range(len(CAMERA_LAYOUT)):
        print("i", i)
        cam_id = CAMERA_LAYOUT[i]

        img = frame_dict[cam_id]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        arucoParameters = aruco.DetectorParameters_create()
        arucoParameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, aruco_dict, parameters=arucoParameters)

        ids = [int(x) for x in ids]
        m_centres = np.empty((4, 2), dtype=np.float32)
        for m_id, c in zip(ids, corners):
            centre_x = (c[0][0][0] + c[0][1][0] +
                        c[0][2][0] + c[0][3][0]) / 4
            centre_y = (c[0][0][1] + c[0][1][1] +
                        c[0][2][1] + c[0][3][1]) / 4
            i = m_id % 4
            m_centres[i] = np.array([centre_x, centre_y])

        if m_centres[0][0] > m_centres[2][0]:
            tmp = m_centres[0].copy()
            m_centres[0] = m_centres[2]
            m_centres[2] = tmp
            tmp = m_centres[1].copy()
            m_centres[1] = m_centres[3]
            m_centres[3] = tmp

        x_origin = m_centres[0][0]
        y_origin = m_centres[0][1]

        print(x_origin, y_origin)
        marker_points = np.array([
            [0, 0],
            [0, 0 + PX_DIST],
            [0 + PX_DIST, 0],
            [0 + PX_DIST, 0 + PX_DIST]
        ], dtype=np.float32)
        T = cv2.getPerspectiveTransform(m_centres, marker_points)

        t_matrices[cam_id] = T
    return t_matrices


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

    print(frame_dict.keys())

    t_matrices = calc_t_matrices(frame_dict)

    print(t_matrices.keys())

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
