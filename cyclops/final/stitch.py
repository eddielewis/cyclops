import argparse
import cv2
import numpy as np


class Stitcher:
    def set_params_from_file(self, fn):
        with np.load(fn, allow_pickle=True) as f:
            self.h_matrices = f["h_matrices"].tolist()
            self.camera_layout = f["camera_layout"].tolist()

    def set_params(self, h_matrices, camera_layout):
        self.h_matrices = h_matrices
        self.camera_layout = camera_layout

    def stitch_h(self, frame_dict, estimate_H):
        if self.h_matrices is None or self.camera_layout is None:
            return None
        stitched_img = frame_dict[self.camera_layout[0]]
        for i in range(len(self.camera_layout)-1):
            cam_a_id = self.camera_layout[i]
            cam_b_id = self.camera_layout[i+1]

            img_b = stitched_img
            img_a = frame_dict[cam_b_id]

            if estimate_H:
                H = estimate_homography([img_a, img_b])
            else:
                m_id = matrix_id(cam_a_id, cam_b_id)
                H = self.h_matrices[m_id]
            stitched_img = stitch_pair_h([img_a, img_b], H)
        return stitched_img

    def stitch_v(self, imgs):
        if self.h_matrices is None or self.camera_layout is None:
            return None
        stitched_img = imgs[0]
        for i in range(1, len(self.camera_layout)-1):
            img_b = stitched_img
            img_a = imgs[i]
            H = estimate_homography([img_a, img_b])
            stitched_img = stitch_pair_v([img_a, img_b], H)
        return stitched_img


def matrix_id(cam_a_id, cam_b_id):
    return cam_a_id + "_" + cam_b_id


def estimate_homography(images, ratio=0.75, reproj_thresh=4.0):
    # unpack the images, then detect keypoints and extract
    # local invariant descriptors from them
    image_a, image_b = images
    kpts_a, features_a = detect_and_describe(image_a)
    kpts_b, features_b = detect_and_describe(image_b)
    # match features between the two images
    match = match_keypoints(kpts_a, kpts_b,
                            features_a, features_b, ratio, reproj_thresh)
    # if the match is None, then there aren't enough matched
    # keypoints to create a panorama
    if match is None:
        return None

    # otherwise, apply a perspective warp to stitch the images
    # together
    (matches, H, status) = match
    return H


def remove_border(stitched_img):
    gray = cv2.cvtColor(stitched_img, cv2.COLOR_BGR2GRAY)
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


def stitch_pair(images, H, w, h):
    img_a, img_b = images
    stitched_img = cv2.warpPerspective(img_a, H, (w, h))
    stitched_img[0:img_b.shape[0], 0:img_b.shape[1]] = img_b
    stitched_img = remove_border(stitched_img)
    return stitched_img


def stitch_pair_h(images, H):
    img_a, img_b = images
    w = img_a.shape[1] + img_b.shape[1]
    h = max(img_a.shape[0], img_b.shape[0])
    return stitch_pair(images, H, w, h)


def stitch_pair_v(images, H):
    img_a, img_b = images
    w = max(img_a.shape[1], img_b.shape[1])
    h = img_a.shape[0] + img_b.shape[0]
    return stitch_pair(images, H, w, h)


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


CAMERA_LAYOUT = ["cyclops1.local", "cyclops0.local"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left_img",
                        type=str)
    parser.add_argument("right_img",
                        type=str)
    args = parser.parse_args()

    left_img = cv2.imread(args.left_img)
    right_img = cv2.imread(args.right_img)

    frame_dict = {
        "cyclops0.local": left_img,
        "cyclops1.local": right_img
    }

    h_matrices = calc_h_matrices(frame_dict)
    stitcher = Stitcher()
    stitcher.set_params(h_matrices, CAMERA_LAYOUT)

    h_img = stitcher.stitch_h(frame_dict)
    cv2.imshow("h img", h_img)

    v_img = stitcher.stitch_v([right_img, left_img])
    cv2.imshow("v img", v_img)

    cv2.waitKey(0)


if __name__ == "__main__":
    main()
