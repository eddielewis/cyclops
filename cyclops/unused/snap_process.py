import cv2 as cv
import time
import sys
import argparse
import os
from picamera.array import PiRGBArray
from picamera import PiCamera
import socket
import errno
from send_multicast import send


HOSTNAME = socket.gethostname()
file_name = ""
snap_count = 0

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(1.0)


def snap(conn, folder, width, height, snap_count, preview):
    try:
        os.makedirs(folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    file_name = "%s/%s_%d_%d_" % (folder, HOSTNAME,
                                  width, height)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array

        if preview:
            cv.imshow('camera', image)

        print(conn.recv())
        if conn.recv() == "snap":
            print("saving")
            save()

        rawCapture.truncate(0)

    cv.destroyAllWindows()
    vs.stop()


def save():
    print("Saving image ", snap_count)
    cv.imwrite("%s%d.jpg" % (file_name, snap_count), image)
    snap_count += 1


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
    parser.add_argument("output_folder",
                        help="Path to folder to save images in.")
    parser.add_argument("--width",
                        default=640,
                        type=int)
    parser.add_argument("--height",
                        default=480,
                        type=int)
    parser.add_argument("--count",
                        default=0,
                        type=int)
    parser.add_argument("--preview",
                        default=true,
                        type=bool)
    args = parser.parse_args()

    snap(args.output_folder, args.width, args.height, args.count)

    print("Files saved")


if __name__ == "__main__":
    main()
