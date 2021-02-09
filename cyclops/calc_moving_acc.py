import json
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

# MARKER_LENGTH = 0.02
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


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
    parser.add_argument("images_folder",
                        help="Path to folder with images in.")
    args = parser.parse_args()

    image_names = glob(args.images_folder + "*.png")

    for image_id, image_name in enumerate(image_names):
        print(image_id, image_name)
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

        data = np.empty((8, 8))

        # iterate through each marker to use as the reference marker
        for ref_marker_count, ref_marker_id in enumerate(ids):
            print("reference marker:", ref_marker_id)
            for marker_count, marker_id in enumerate(ids):
                print("\n")
                #  project the points of the marker using the rvecs and tvecs of that marker
                marker_image_points, _ = cv2.projectPoints(
                    obj_points, rvecs[marker_count], tvecs[marker_count], camera_matrix, dist_coefs)

                est_obj_points = obj_points.copy()

                # don't translate the reference marker
                if marker_id != ref_marker_id:
                    # iterate through the 4 corners
                    # estimate the markers points by translating the points of the reference marker
                    est_obj_points += vectors[marker_id[0]]
                    est_obj_points -= vectors[ref_marker_id[0]]

                # project the points of the estimated marker position using rvecs and tvecs of reference marker
                est_image_points, _ = cv2.projectPoints(
                    est_obj_points, rvecs[ref_marker_count], tvecs[ref_marker_count], camera_matrix, dist_coefs)

                # project the points of the reference marker using its own rvecs and tvecs
                # this (virtual) marker has a known position so we can estimate the pixels per mm
                cmp_image_points, _ = cv2.projectPoints(
                    obj_points, rvecs[ref_marker_count], tvecs[ref_marker_count], camera_matrix, dist_coefs)

                # calc distance between the pixels of the cmp marker and the reference marker
                # within the reference marker's coordinate system
                cmp_dist_px = sum([np.linalg.norm(a-b)
                                   for a, b in zip(est_image_points, cmp_image_points)]) / 4
                print("pixel distance:", cmp_dist_px)

                # calc distance distance between the vectors of the cmp and reference marker
                cmp_dist_m = sum([np.linalg.norm(a-b)
                                  for a, b in zip(est_obj_points, obj_points)]) / 4
                print("metres distance", cmp_dist_m)

                px_per_mm = 0.0
                try:
                    px_per_mm = cmp_dist_px / (cmp_dist_m * 1000)
                    print("pixels per mm estimate: %f" % px_per_mm)
                except:
                    pass

                abs_inaccuracy_px = sum([np.linalg.norm(a-b)
                                         for a, b in zip(est_image_points, marker_image_points)]) / 4

                print("px inaccuracy of marker %d with ref %d: %f" %
                      (marker_id, ref_marker_id, abs_inaccuracy_px))
                abs_inaccuracy_mm = abs_inaccuracy_px / px_per_mm
                print("mm inaccuracy of marker %d with ref %d: %f" %
                      (marker_id, ref_marker_id, abs_inaccuracy_mm))

                # Take array in the form [[x, y], [x,y]] and produce [[x,x], [y,y]]
                x, y = marker_image_points.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="b", label=str(marker_id))
                plt.annotate(str(marker_id), (x[0], y[0]))

                x, y = est_image_points.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="r", label=str(marker_id))
                plt.annotate(str(marker_id), (x[-1], y[-1]))

                data[ref_marker_id, marker_id] = abs_inaccuracy_px

            plt.ylim(0, 480)
            plt.xlim(0, 640)
            plt.gca().set_aspect('equal', adjustable='box')
            # plt.legend(loc="upper left")
            plt.title("image %d reference %d" % (image_id, ref_marker_id))
            # plt.show()
            plt.savefig("img_%d_ref_%d.png" % (image_id, ref_marker_id))
            plt.close()

        # Write an example CSV file with headers on first line
        with open("%d_data.csv" % image_id, 'w') as fp:
            np.savetxt(fp, data, '%s', ',')


if __name__ == "__main__":
    main()
