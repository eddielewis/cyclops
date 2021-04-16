import numpy as np
import argparse
import cv2


def estimate_homography(images, ratio=0.75, reprojThresh=4.0):
    # unpack the images, then detect keypoints and extract
    # local invariant descriptors from them
    image_b, image_a = images
    kpts_a, features_a = detectAndDescribe(image_a)
    kpts_b, features_b = detectAndDescribe(image_b)
    # match features between the two images
    M = matchKeypoints(kpts_a, kpts_b,
                       features_a, features_b, ratio, reprojThresh)
    # if the match is None, then there aren't enough matched
    # keypoints to create a panorama
    if M is None:
        return None

    # otherwise, apply a perspective warp to stitch the images
    # together
    (matches, H, status) = M

    if draw_matches:
        return H, draw_matches(
            image_a, image_b, kpts_a, kpts_b, matches, status)
    return H


def detectAndDescribe(image):
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


def matchKeypoints(kpts_a, kpts_b, features_a, features_b,
                   ratio, reprojThresh):
    # compute the raw matches and initialize the list of actual
    # matches
    matcher = cv2.DescriptorMatcher_create("BruteForce")
    rawMatches = matcher.knnMatch(features_a, features_b, 2)
    matches = []
    # loop over the raw matches
    for m in rawMatches:
        # ensure the distance is within a certain ratio of each
        # other (i.e. Lowe's ratio test)
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            matches.append((m[0].trainIdx, m[0].queryIdx))

    # computing a homography requires at least 4 matches
    if len(matches) > 4:
        # construct the two sets of points
        ptsA = np.float32([kpts_a[i] for (_, i) in matches])
        ptsB = np.float32([kpts_a[i] for (i, _) in matches])
        # compute the homography between the two sets of points
        (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                                         reprojThresh)
        # return the matches along with the homograpy matrix
        # and status of each matched point
        return (matches, H, status)
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


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
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

    left = cv2.imread(args.left)
    right = cv2.imread(args.right)
    fn = args.out

    H, matches = estimate_homography([left, right])

    np.savez(fn, H=H)
    print("Homography matrix saved as", fn)

    cv2.imshow("Matches", matches)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
