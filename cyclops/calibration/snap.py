import cv2 as cv
import time
import sys
import argparse
import os
from imutils.video import VideoStream


def snap(folder, camera_id, width, height):
    vs = VideoStream(usePiCamera=True, resolution=(
        width, height), framerate=80).start()
    time.sleep(2.0)
    try:
        os.makedirs(folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    snap_count = 0

    file_name = "%s/%s_%d_%d_" % (folder, camera_id,
                                  width, height)
    while(True):
        image = vs.read()

        cv.imshow('camera', image)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord(' '):
            print("Saving image ", snap_count)
            cv.imwrite("%s%d.jpg" % (file_name, snap_count), image)
            snap_count += 1

    cv.destroyAllWindows()
    vs.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Saves image from the camera. Press q to quit and spacebar to save the snapshot")
    parser.add_argument("output_folder",
                        help="Path to folder to save images in.")
    parser.add_argument("camera_id",
                        help="An id for this camera to keep track of calibration images.")
    parser.add_argument("--width",
                        default=640,
                        type=int)
    parser.add_argument("--height",
                        default=480,
                        type=int)
    args = parser.parse_args()

    snap(args.output_folder, args.camera_id, args.width, args.height)

    print("Files saved")


if __name__ == "__main__":
    main()
