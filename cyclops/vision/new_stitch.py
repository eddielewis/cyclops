import cv2.aruco as aruco
from glob import glob
import argparse
import numpy as np
import imutils
import cv2


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

    stitched_img = images[0]
    for a in range(1, len(images)):
        image_b = stitched_img
        image_a = images[a]
        stitched_img = stitch_pair(image_a, image_b, H)
    return stitched_img


# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("left",
                    help="Path to left-hand image",
                    type=str)
parser.add_argument("right",
                    help="Path to right-hand image",
                    type=str)
parser.add_argument("out",
                    help="Filename for the resulting H matrix",
                    type=str)
args = parser.parse_args()

img_a = cv2.imread(args.left)
img_b = cv2.imread(args.right)

img_a = imutils.resize(img_a, width=400)
img_b = imutils.resize(img_b, width=400)

fn = args.out

# undistort the images
# img_a = cv2.undistort(img_a, camera_matrix, dist_coefs)
# img_b = cv2.undistort(img_b, camera_matrix, dist_coefs)

gray = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
arucoParameters = aruco.DetectorParameters_create()
corners1, ids, rejectedImgPoints = aruco.detectMarkers(
    gray, aruco_dict, parameters=arucoParameters)


a_centres = np.empty((3, 2), dtype=np.float32)
for i, c in enumerate(corners1):
    centre_x = (c[0][0][0] + c[0][1][0] +
                c[0][2][0] + c[0][3][0]) / 4
    centre_y = (c[0][0][1] + c[0][1][1] +
                c[0][2][1] + c[0][3][1]) / 4
    a_centres[i] = np.array([centre_x, centre_y])
print(ids)

gray = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
arucoParameters = aruco.DetectorParameters_create()
corners2, ids, rejectedImgPoints = aruco.detectMarkers(
    gray, aruco_dict, parameters=arucoParameters)
print(ids)

b_centres = np.empty((3, 2), dtype=np.float32)
for i, c in enumerate(corners2):
    centre_x = (c[0][0][0] + c[0][1][0] +
                c[0][2][0] + c[0][3][0]) / 4
    centre_y = (c[0][0][1] + c[0][1][1] +
                c[0][2][1] + c[0][3][1]) / 4
    b_centres[i] = np.array([centre_x, centre_y])

print(a_centres[2][1].flags)
# print(a_centres.checkVector(2, cv2.CV_32F) == 3)


pts1 = np.float32([[50, 50], [200, 50], [50, 200]])
pts2 = np.float32([[10, 100], [200, 50], [100, 250]])

print(a_centres)
print(pts1)
print(a_centres.shape)
print(pts1.shape)
print(type(a_centres[0]))
print(type(pts1[0]))

M = cv2.getAffineTransform(a_centres, pts2)
print(M)


print(corners1[0].shape)
print("oeuifhesfuisefhuio")
print(corners1[0][0, :3, :])
T = cv2.getAffineTransform(corners1[2][0, :3, :], corners2[2][0, :3, :])
print(T)

""" stitched_img = cv2.warpPerspective(
    image_a, H, (image_a.shape[1] + image_b.shape[1],
                 max(image_a.shape[0], image_b.shape[0]))) """

bob = cv2.warpAffine(img_b, T, (img_b.shape[1], img_b.shape[0]))
print(bob.shape)
jim = np.empty((img_a.shape[0], img_a.shape[1] + bob.shape[1], 3))
print(jim.shape)
bob = np.concatenate((img_a, bob), axis=1)
cv2.imshow("bob", bob)
cv2.waitKey(0)
