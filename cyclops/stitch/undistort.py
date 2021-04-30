import argparse
import numpy as np
import cv2

"""
Undistorts the image supplied in program arugment with camera matrix specified.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path",
                        help="Path to the image",
                        type=str)
    parser.add_argument("camera_matrix_path",
                        help="Path to saved camera matrix",
                        type=str)
    args = parser.parse_args()

    with np.load(args.camera_matrix_path) as f:
        camera_matrix, dist_coefs, rvecs, tvecs = [f[i] for i in (
            'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]
    img = cv2.imread(args.image_path)

    undistorted_img = cv2.undistort(img, camera_matrix, dist_coefs)
    cv2.imwrite(args.image_path[:-4] +
                "_undistorted" + args.image_path[-4:], img)


if __name__ == "__main__":
    main()
