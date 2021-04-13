import numpy as np
import cv2
import cv2.aruco as aruco
import time
from load_camera_matrix import camera_matrix, dist_coefs
import argparse
from glob import glob
import matplotlib.pyplot as plt

"""
    load images
    detect
    pose estimate

    compare others according to one markers coords
    calc absolute inaccuracy
    repeat for each marker
"""

MARKER_LENGTH = 0.0185
MARKER_DISTANCE = 0.047

vectors = [
    x * MARKER_DISTANCE for x in [
        np.array((0, 0, 0)),
        np.array((1, 0, 0)),
        np.array((0, -1, 0)),
        np.array((1, -1, 0)),
        np.array((2, 0, 0)),
        np.array((2, -1, 0)),
        np.array((3, 0, 0)),
        np.array((3, -1, 0))
    ]
]

image_vectors = [
    x * MARKER_DISTANCE for x in [
        np.array((0, 0.00, 0)),
        np.array((0, 2, 0)),
        np.array((0, 4, 0))
    ]
]


def compare_markers(marker_id, rvecs_list, tvecs_list, obj_points):
    total_inaccuracy_px_list = np.zeros((3, 3))
    for ref_marker_id, (ref_rvecs, ref_tvecs) in enumerate(zip(rvecs_list, tvecs_list)):
        inaccuracy_px_list = np.zeros(3)
        for cmp_marker_id, (cmp_rvecs, cmp_tvecs) in enumerate(zip(rvecs_list, tvecs_list)):
            if cmp_marker_id == ref_marker_id:
                continue
            marker_image_points, _ = cv2.projectPoints(
                obj_points, cmp_rvecs, cmp_tvecs, camera_matrix, dist_coefs)
            est_obj_points = obj_points.copy()
            if cmp_marker_id != ref_marker_id:
                est_obj_points += image_vectors[cmp_marker_id]
                est_obj_points -= image_vectors[ref_marker_id]
            est_image_points, _ = cv2.projectPoints(
                est_obj_points, ref_rvecs, ref_tvecs, camera_matrix, dist_coefs)
            inaccuracy_px = sum([np.linalg.norm(a-b)
                                 for a, b in zip(est_image_points, marker_image_points)]) / 4
            inaccuracy_px_list[cmp_marker_id] = inaccuracy_px

            x, y = marker_image_points.flatten("F").reshape(2, -1)
            plt.scatter(x, y, c="b", label=str(cmp_marker_id))
            plt.annotate(str(cmp_marker_id), (x[0], y[0]))

            x, y = est_image_points.flatten("F").reshape(2, -1)
            plt.scatter(x, y, c="r", label=str(cmp_marker_id))
            plt.annotate(str(cmp_marker_id), (x[-1], y[-1]))

        total_inaccuracy_px_list[ref_marker_id] = inaccuracy_px_list

    plt.ylim(0, 480)
    plt.xlim(0, 640)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.legend(loc="upper left")
    plt.title("reference %d" % (marker_id))
    # plt.show()
    plt.savefig("ref_%d.png" % (marker_id))
    plt.close()
    return total_inaccuracy_px_list


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
    parser.add_argument("images_folder",
                        help="Path to folder with images in.")
    args = parser.parse_args()

    image_names = glob(args.images_folder + "*.png")

    rvecs_list, tvecs_list, obj_points, ids = np.empty(
        (8, 3, 1, 3)), np.empty((8, 3, 1, 3)), None, []

    image_data = []

    for image_name in image_names:
        image_id = int(image_name[-5:-4])
        print(image_id)
        image = cv2.imread(image_name)
        # pre-process
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        arucoParameters = aruco.DetectorParameters_create()
        # detect markers
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, aruco_dict, parameters=arucoParameters)
        image = aruco.drawDetectedMarkers(image, corners)
        # pose estimate all markers
        rvecs, tvecs, obj_points = aruco.estimatePoseSingleMarkers(
            corners, MARKER_LENGTH, camera_matrix, dist_coefs)
        data = {}
        for marker_count, marker_id in enumerate(ids):
            rvecs_list[marker_id, image_id] = rvecs[marker_count]
            tvecs_list[marker_id, image_id] = tvecs[marker_count]

    image_count = len(image_names)

    for marker_id in range(len(rvecs_list)):
        inaccuracy_px_list = compare_markers(
            marker_id, rvecs_list[marker_id], tvecs_list[marker_id], obj_points)
        print(inaccuracy_px_list)

        # Write an example CSV file with headers on first line
        with open("moving_%d_data.csv" % marker_id, 'w') as fp:
            np.savetxt(fp, inaccuracy_px_list, '%s', ',')


if __name__ == "__main__":
    main()
