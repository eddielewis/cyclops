from glob import glob
import argparse
import numpy as np
import imutils
import cv2


def estimate_H(image_a, image_b, ratio=0.75, reproj_thresh=4.0):

    (keypoints_a, features_a) = detect_and_describe(image_a)
    (keypoints_b, features_b) = detect_and_describe(image_b)
    # match features between the two images
    match = match_keypoints(
        keypoints_a, keypoints_b, features_a, features_b, ratio, reproj_thresh)
    # if the match is None, then there aren't enough matched
    # keypoints to create a panorama
    if match is None:
        return None
    # otherwise, apply a perspective warp to stitch the images
    # together
    matches, H, status = match
    return H


def stitch(image_a, image_b, H):
    result = cv2.warpPerspective(image_a, H,
                                 (image_a.shape[1] + image_b.shape[1], image_a.shape[0]))
    result[0:image_b.shape[0], 0:image_b.shape[1]] = image_b
    return result


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
            ptA = (int(kps_a[queryIdx][0]), int(kps_a[queryIdx][1]))
            ptB = (int(kps_b[trainIdx][0]) + w_a, int(kps_b[trainIdx][1]))
            cv2.line(vis, ptA, ptB, (0, 255, 0), 1)
    # return the visualization
    return vis


# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("images_folder",
                    help="Path to the images folder")
args = parser.parse_args()
image_names = ["0", "1", "2"]
image0 = cv2.imread(args.images_folder + image_names[0] + ".jpg")
image1 = cv2.imread(args.images_folder + image_names[1] + ".jpg")
image2 = cv2.imread(args.images_folder + image_names[2] + ".jpg")

image0 = imutils.resize(image0, width=400)
image1 = imutils.resize(image1, width=400)
image2 = imutils.resize(image2, width=400)

H01 = estimate_H(image0, image1)
print("H01")
H12 = estimate_H(image1, image2)
print("H12")


img = stitch(image2, image1, H12)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

thrs = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(
    gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
largest_a = 0
largest_a_index = 0

for i, c in enumerate(contours):
    a = cv2.contourArea(c, False)
    if a > largest_a:
        largest_a = a
        largest_a_index = i
bounding_rect = cv2.boundingRect(contours[largest_a_index])

print("before img")

print(bounding_rect)

x, y, width, height = bounding_rect

img = img[y:height, x:width]


# Do with other images now
img2 = stitch(image1, image0, H01)
gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

thrs = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(
    gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
largest_a = 0
largest_a_index = 0

for i, c in enumerate(contours):
    a = cv2.contourArea(c, False)
    if a > largest_a:
        largest_a = a
        largest_a_index = i
        bounding_rect = cv2.boundingRect(c)

x, y, width, height = bounding_rect

img2 = img2[y:height, x:width]


cv2.imshow("1 and 2", img)
cv2.imshow("0 and 1", img2)
# cv2.waitKey(0)

H012 = estimate_H(img, img2)
img4 = stitch(img, img2, H012)

cv2.imshow("last", img4)

gray = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY)

thrs = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(
    gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
largest_a = 0
largest_a_index = 0

for i, c in enumerate(contours):
    a = cv2.contourArea(c, False)
    if a > largest_a:
        largest_a = a
        largest_a_index = i
        bounding_rect = cv2.boundingRect(c)

x, y, width, height = bounding_rect

img4 = img4[y:height, x:width]

cv2.imshow("last 2", img4)

cv2.waitKey(0)
