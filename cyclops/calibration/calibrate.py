import numpy as np
import cv2
import argparse
import sys
import getopt
from glob import glob
import os
import errno
import socket

THREADS = 4
CAMERA_ID = socket.gethostname()


def split_filename(filename):
    path, filename = os.path.split(filename)
    name, ext = os.path.splitext(filename)
    return path, name, ext


def calibrate(images_folder, square_size, sensor_mode, threads):

    image_mask = images_folder + "*.jpg"
    output_folder = images_folder[:-1] + "_output/"
    print(output_folder)

    image_names = glob(image_mask)

    pattern_size = (9, 6)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size

    obj_points = []
    image_points = []
    h, w = cv2.imread(image_names[0], cv2.IMREAD_GRAYSCALE).shape[:2]

    def process_image(filename):
        print('processing %s... ' % filename)
        image = cv2.imread(filename, 0)
        if image is None:
            print("Failed to load", filename)
            return None

        assert w == image.shape[1] and h == image.shape[0], ("size: %d x %d ... " % (
            image.shape[1], image.shape[0]))
        found, corners = cv2.findChessboardCorners(image, pattern_size)
        if found:
            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
            cv2.cornerSubPix(image, corners, (5, 5), (-1, -1), term)

        if output_folder:
            vis = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            _path, name, _ext = split_filename(filename)

            outfile = os.path.join(output_folder, name + '_chess.png')
            cv2.imwrite(outfile, vis)

        if not found:
            print('chessboard not found')
            return None
        print('           %s... OK' % filename)
        return (corners.reshape(-1, 2), pattern_points)

    if threads <= 1:
        chessboards = [process_image(filename) for filename in image_names]
    else:
        print("Run with %d threads..." % THREADS)
        from multiprocessing.dummy import Pool as ThreadPool
        pool = ThreadPool(THREADS)
        chessboards = pool.map(process_image, image_names)

    chessboards = [x for x in chessboards if x is not None]
    for (corners, pattern_points) in chessboards:
        image_points.append(corners)
        obj_points.append(pattern_points)

    # calculate camera distortion
    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, image_points, (w, h), None, None)

    print("\nRMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: ", dist_coefs.ravel())

    matrix_output_folder = output_folder[:-1] + "/matrix/"
    try:
        # create directories for the matrix and the new images
        os.makedirs(matrix_output_folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    np.savez('%s/matrix_%s_%s' % (matrix_output_folder, CAMERA_ID, sensor_mode), camera_matrix=camera_matrix,
             dist_coefs=dist_coefs, rvecs=rvecs, tvecs=tvecs)

    # undistort the image with the calibration
    print('')
    for filename in image_names:
        path, name, ext = split_filename(filename)
        image_found = os.path.join(output_folder, name + '_chess.png')
        outfile = os.path.join(output_folder, name + '_undistorted.png')

        image = cv2.imread(image_found)
        if image is None:
            continue

        h, w = image.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv2.undistort(image, camera_matrix,
                            dist_coefs, None, new_camera_matrix)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        print('Undistorted image written to: %s' % outfile)
        cv2.imwrite(outfile, dst)


def main():
    parser = argparse.ArgumentParser(
        description="Uses images from folder specified to calculate camera calibration matrix.")
    parser.add_argument("images_folder",
                        help="Path to folder containing images.")
    parser.add_argument("square_size",
                        help="The size of squares on the chessboard",
                        type=float)
    parser.add_argument("sensor_mode",
                        help="The sensor mode used to capture calibration images. Docs can be found here: https://picamera.readthedocs.io/en/latest/fov.html#sensor-modes",
                        type=int)
    parser.add_argument("--threads",
                        default=THREADS,
                        type=int)
    args = parser.parse_args()

    calibrate(args.images_folder,
              args.square_size, args.sensor_mode, args.threads)


if __name__ == "__main__":
    main()
