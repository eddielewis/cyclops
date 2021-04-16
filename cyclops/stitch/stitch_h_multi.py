import argparse
import numpy as np
import cv2
import imutils


def estimate_homography(images, ratio=0.75, reproj_thresh=4.0, show_matches=False):
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
    if show_matches:
        return H, draw_matches(
            image_a, image_b, kpts_a, kpts_b, matches, status)
    return H

# TODO undistort images first


def stitch(images, H=None, ratio=0.85, reproj_thresh=4.0, show_matches=False):
    def stitch_pair(image_a, image_b, H):
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
            image_a, H, (1, 1))

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

    stitched_img = images[0]
    for a in range(1, len(images)):
        image_b = stitched_img
        image_a = images[a]
        stitched_img = stitch_pair(image_a, image_b, H)
    return stitched_img


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


def draw_matches(image_a, image_b, kps_a, kps_b, matches, status):
    # initialize the output visualization image
    (h_a, w_a) = image_a.shape[:2]
    (h_b, w_b) = image_b.shape[:2]
    vis = np.zeros((max(h_a, h_b), w_a + w_b, 3), dtype="uint8")
    vis[0:h_a, 0:w_a] = image_a
    vis[0:h_b, w_a:] = image_b
    # loop over the matches
    for ((trainIdx, queryIdx), s) in zip(matches, status):
        # only process the match if the keypoint was successfully
        # matched
        if s == 1:
            # draw the match
            pt_a = (int(kps_a[queryIdx][0]), int(kps_a[queryIdx][1]))
            pt_b = (int(kps_b[trainIdx][0]) + w_a, int(kps_b[trainIdx][1]))
            cv2.line(vis, pt_a, pt_b, (0, 255, 0), 1)
    # return the visualization
    return vis


# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("images_folder",
                    help="Path to the images folder")
parser.add_argument("--H",
                    help="Path to saved homography matrix",
                    type=str)
args = parser.parse_args()

image_names = ["0", "1"]
# image_names = ["0", "1", "2", "3", "4", "5"]
images = [cv2.imread(args.images_folder + name + ".png")
          for name in image_names]
images = [imutils.resize(image, width=400) for image in images]

# H, matches = estimate_homography(images, show_matches=True)
# cv2.imshow("matches", matches)
if args.H:
    with np.load(args.H) as f:
        H = f["H"]
        result = stitch(images, H=H)
else:
    H = estimate_homography(images)
    result = stitch(images, H=H)


# cv2.imshow("Keypoint Matches", vis)
cv2.imshow("Result", result)
cv2.waitKey(0)
