import imutils
import argparse
import cv2
import cv2.aruco as aruco
import numpy as np
from .setup_params import PX_DIST


# Constant that determines the width and height of the stitched image
PX_DIST = 480


class Stitcher:
    def set_params_from_file(self, fn):
        with np.load(fn, allow_pickle=True) as f:
            self.t_matrices = f["t_matrices"].tolist()
            self.camera_layout = f["camera_layout"].tolist()

    def set_params(self, t_matrices, camera_layout):
        self.h_matrices = t_matrices
        self.camera_layout = camera_layout

    def stitch_h(self, frame_dict):
        """
        Stitches the images horizontally, using the pre-calculated transformation matrices
        frame_dict is a dict of camera id and frame.
        """
        # Pre-calculated matrices are required
        if self.t_matrices is None or self.camera_layout is None:
            return None

        # Once transformed, images are put in a list to be concatenated
        imgs = []
        for cam_id, img in frame_dict.items():
            # Gets the pre-calculated matrix from the object attribute
            T = self.t_matrices[cam_id]
            img = cv2.warpPerspective(
                img, T, (img.shape[1], img.shape[0]))
            # Crops the region outside the marker centres
            corrected_img = img[:PX_DIST, :PX_DIST]
            img.append(corrected_img)

        # Stacks all the images horizontally into one array
        stitched_img = np.hstack(imgs)
        return stitched_img

    def stitch_v(self, imgs):
        """
        Stitches the images vertically
        All processing is done when stitching the images horizontally,
        so they must simply be stacked on top of each other
        """
        if self.t_matrices is None or self.camera_layout is None:
            return None
        return np.vstack(imgs)


def calc_marker_centre(corners):
    """
    Returns the centre of the marker from an avg of the marker points
    """
    c = corners
    x = (c[0][0][0] + c[0][1][0] +
         c[0][2][0] + c[0][3][0]) / 4
    y = (c[0][0][1] + c[0][1][1] +
         c[0][2][1] + c[0][3][1]) / 4
    return [x, y]


def find_markers(img):
    """
    Finds any markers in the image and returns their corners and ids.
    """
    # Function requires grayscale image as specified in paper
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Define the marker dictionary used
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    arucoParameters = aruco.DetectorParameters_create()
    # Yields a greater corner accuracy in testing than the default method
    arucoParameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    return ids, corners


def calc_t_matrices(frame_dict):
    """
    Generates the perspective transformation matrices to be used for stitching
    """
    t_matrices = {}

    for i in range(len(CAMERA_LAYOUT)-1):
        cam_id = CAMERA_LAYOUT[i]

        img = frame_dict[cam_id]
        # Gets marker corners and ids from a function in the aruco module
        corners, ids = find_markers(img)

        # ids is a list of single element list
        # this converts each list to an int
        ids = [int(x) for x in ids]
        m_centres = np.empty((4, 2), dtype=np.float32)
        for m_id, c in zip(ids, corners):
            centre = calc_marker_centre(c)
            i = m_id % 4
            m_centres[i] = np.array(centre)
        # Puts the marker centres at the correct indexes
        # top-left: 0
        # bottom-left: 1
        # top-right: 2
        # bottom-right: 3
        if m_centres[0][0] > m_centres[2][0]:
            tmp = m_centres[0].copy()
            m_centres[0] = m_centres[2]
            m_centres[2] = tmp
            tmp = m_centres[1].copy()
            m_centres[1] = m_centres[3]
            m_centres[3] = tmp

        # Creates img points to transform the marker centre points to
        # The order is top-left, bottom-left, top-right, bottom-right
        marker_points = np.array([
            [0, 0],
            [0, 0 + PX_DIST],
            [0 + PX_DIST, 0],
            [0 + PX_DIST, 0 + PX_DIST]
        ], dtype=np.float32)
        T = cv2.getPerspectiveTransform(m_centres, marker_points)

        t_matrices[cam_id] = T
    return t_matrices


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
    left_img = imutils.resize(left_img, width=400)
    right_img = imutils.resize(right_img, width=400)

    frame_dict = {
        "cyclops0.local": left_img,
        "cyclops1.local": right_img
    }

    h_matrices = calc_t_matrices(frame_dict)
    stitcher = Stitcher()
    stitcher.set_params(h_matrices, CAMERA_LAYOUT)

    h_img = stitcher.stitch_h(frame_dict, False)
    cv2.imshow("h img", h_img)

    v_img = stitcher.stitch_v([right_img, left_img])
    cv2.imshow("v img", v_img)

    cv2.waitKey(0)


if __name__ == "__main__":
    main()
