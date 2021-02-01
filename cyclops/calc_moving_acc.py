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

ids = [0, 1, 2, 3, 4, 5, 6, 7]

vectors = [
    np.array((0.00, 0.00, 0.00)),
    np.array((0.00, 0.05, 0.00)),
    np.array((0.05, 0.00, 0.00)),
    np.array((0.05, 0.05, 0.00)),
    np.array((0.10, 0.00, 0.00)),
    np.array((0.10, 0.05, 0.00)),
    np.array((0.15, 0.00, 0.00)),
    np.array((0.15, 0.05, 0.00))
]

MARKER_LENGTH = 0.02


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
    parser.add_argument("images_folder",
                        help="Path to folder with images in.")
    args = parser.parse_args()

    image_names = glob(args.images_folder + "*")
    images = [cv2.imread(x) for x in image_names]

    for image_id, image in enumerate(images):
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

        # iterate through each marker to use as the reference marker
        for id_ref in ids:
            id_ref = int(id_ref)
            print("reference marker:", id_ref)
            for id in ids:
                print("\n")
                id = int(id)
                #  project the points of the marker using the rvecs and tvecs of that marker
                marker_image_points, _ = cv2.projectPoints(
                    obj_points, rvecs[id], tvecs[id], camera_matrix, dist_coefs)

                est_obj_points = obj_points.copy()

                # don't translate the reference marker
                if id != id_ref:
                    # iterate through the 4 corners
                    # estimate the markers points by translating the points of the reference marker
                    est_obj_points += vectors[id]
                    est_obj_points -= vectors[id_ref]

                # project the points of the estimated marker position using rvecs and tvecs of reference marker
                est_image_points, _ = cv2.projectPoints(
                    est_obj_points, rvecs[id_ref], tvecs[id_ref], camera_matrix, dist_coefs)

                # project the points of the reference marker using its own rvecs and tvecs
                # this (virtual) marker has a known position so we can estimate the pixels per mm
                cmp_image_points, _ = cv2.projectPoints(
                    obj_points, rvecs[id_ref], tvecs[id_ref], camera_matrix, dist_coefs)

                # calc distance between the pixels of the cmp marker and the reference marker
                # within the reference marker's coordinate system
                dist_px = sum([np.linalg.norm(a-b)
                               for a, b in zip(est_image_points, cmp_image_points)]) / 4
                print("pixel distance:", dist_px)

                # calc distance distance between the vectors of the cmp and reference marker
                dist_m = sum([np.linalg.norm(a-b)
                              for a, b in zip(est_obj_points, obj_points)]) / 4
                print("metres distance", dist_m)

                try:
                    px_per_mm = dist_px / (dist_m * 1000)
                    print("pixels per mm estimate: %f" % px_per_mm)
                except:
                    pass

                abs_inaccuracy_px = sum([np.linalg.norm(a-b)
                                         for a, b in zip(est_image_points, marker_image_points)]) / 4
                print("px inaccuracy of marker %d with ref %d: %f" %
                      (id, id_ref, abs_inaccuracy_px))
                abs_inaccuracy_mm = abs_inaccuracy_px * px_per_mm
                print("mm inaccuracy of marker %d with ref %d: %f" %
                      (id, id_ref, abs_inaccuracy_mm))

                x, y = marker_image_points.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="b", label=str(id))

                x, y = est_image_points.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="r", label=str(id))

                plt.annotate(str(id), (x[-1], y[-1]))

            plt.ylim(0, 480)
            plt.xlim(0, 640)
            plt.gca().set_aspect('equal', adjustable='box')
            plt.legend(loc="upper left")
            plt.title("image %s reference %d" % (image_id, id_ref))
            plt.show()


if __name__ == "__main__":
    main()
