import argparse
import json
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
    np.savez('H', H=H)
    print("Saved homography matrix as H.npz")
    return H


def stitch(image_a, image_b, H, ratio=0.85, reproj_thresh=4.0,):
    def stitch_pair(H):
        if H is None:
            print("Calculating homogprahy matrix")
            keypoints_a, features_a = detect_and_describe(image_a)
            keypoints_b, features_b = detect_and_describe(image_b)
            # match features between the two images
            match = match_keypoints(
                keypoints_a, keypoints_b, features_a, features_b, ratio, reproj_thresh)
            # if the match is None, then there aren't enough matched
            # keypoints to create a panorama
            if match is None:
                print("Not enough keypoints")
                return None
            # otherwise, apply a perspective warp to stitch the images
            # together
            (matches, H, status) = match
        stitched_img = cv2.warpPerspective(
            image_a, H, (image_a.shape[1] + image_b.shape[1],
                         max(image_a.shape[0], image_b.shape[0])))

        stitched_img[0:image_b.shape[0], 0:image_b.shape[1]] = image_b
        gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
        # thrs = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(
            gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        max_a, max_a_index = 0, 0
        for i in range(0, len(contours)):
            a = cv2.contourArea(contours[i], False)
            if a > max_a:
                max_a = a
                max_a_index = i
        bounding_rect = cv2.boundingRect(contours[max_a_index])
        x, y, width, height = bounding_rect
        stitched_img = stitched_img[y:height, x:width]
        return stitched_img
    stitched_img = stitch_pair(H)
    cv2.imwrite("stitch.png", stitched_img)
    print("written")


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


H = None

# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("--H",
                    help="Path to saved homography matrix",
                    type=str)
args = parser.parse_args()

if args.H:
    with np.load(args.H) as f:
        H = f["H"]

# loop over until Keyboard Interrupted
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
        camera_id, frame_count = data["camera_id"], data["frame_count"]
        if frame_dict.get(frame_count) is None:
            frame_dict[frame_count] = {
                camera_id: frame
            }
        else:
            frame_dict[frame_count][camera_id] = frame

        if len(frame_dict[frame_count].keys()) == CAMERA_COUNT:
            print("len")
            if H is None:
                print("H none")
                H = estimate_homography(frame_dict[frame_count].values())
                print(H)
            image_a, image_b = [
                x for x in frame_dict[frame_count].values()]
            stitch(image_a, image_b, H)
            print("stitched")

        # get extracted frame's shape
        # (h, w) = frame.shape[:2]
        # update the extracted frame in the received frame dictionary
        # build a montage using data dictionary
        # montages = build_montages(frame_dict.values(), (w, h), (2, 1))
        # display the montage(s) on the screen
        # for (i, montage) in enumerate(montages):
        # cv2.imshow("Montage Footage {}".format(i), montage)

        # check for 'q' key if pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    except KeyboardInterrupt:
        break

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()
