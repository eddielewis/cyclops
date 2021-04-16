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

# Define received frame dictionary
frame_dict = {}
CAMERA_COUNT = 2


def estimate_homography(images, ratio=0.75, reproj_thresh=4.0):
    # unpack the images, then detect keypoints and extract
    # local invariant descriptors from them
    image_b, image_a = images
    kpts_a, features_a = detect_and_describe(image_a)
    kpts_b, features_b = detect_and_describe(image_b)
    # match features between the two images
    M = match_keypoints(kpts_a, kpts_b,
                        features_a, features_b, ratio, reproj_thresh)
    # if the match is None, then there aren't enough matched
    # keypoints to create a panorama
    if M is None:
        return None

    # otherwise, apply a perspective warp to stitch the images
    # together
    (matches, H, status) = M
    return H


def detect_and_describe(image):
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # detect and extract features from the image
    descriptor = cv2.SIFT_create()
    (kps, features) = descriptor.detectAndCompute(image, None)
    # convert the keypoints from KeyPoint objects to NumPy
    # arrays
    kps = np.float32([kp.pt for kp in kps])
    # return a tuple of keypoints and features
    return (kps, features)


def match_keypoints(kps_a, kps_b, features_a, features_b,
                    ratio, reproj_thresh):
    # compute the raw matches and initialize the list of actual
    # matches
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    raw_matches = matcher.knnMatch(features_a, features_b, 2)
    matches = []
    # loop over the raw matches
    for m in raw_matches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    # computing a homography requires at least 4 matches
    if len(matches) > 4:
        # construct the two sets of points
        ptsA = np.float32([kps_a[i] for (_, i) in matches])
        ptsB = np.float32([kps_b[i] for (i, _) in matches])
        # compute the homography between the two sets of points
        (h_matrix, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                                                reproj_thresh)
        # return the matches along with the homograpy matrix
        # and status of each matched point
        return (matches, h_matrix, status)
    # otherwise, no homograpy could be computed
    return None


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
    h_matrices[cam_a_id + "_" + cam_b_id] = H
np.savez('h_matrices.npz', h_matrices=h_matrices)
print("Saved matrices")

client.close()
