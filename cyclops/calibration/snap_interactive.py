import cv2 as cv
import time
import sys
import argparse
import os
from vidgear.gears import PiGear
import socket
import errno

HOSTNAME = socket.gethostname()


def snap(folder, width, height, snap_count):
    options = {
        "hflip": True,
        "exposure_mode": "auto",
        "iso": 800,
        "exposure_compensation": 15,
        "awb_mode": "horizon",
        "sensor_mode": 4
    }
    stream = PiGear(resolution=(1600, 1200), framerate=30,
                    logging=True, **options).start()
    time.sleep(2.0)
    try:
        os.makedirs(folder)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    file_name = "%s/%s_%d_%d_" % (folder, HOSTNAME,
                                  width, height)
    while(True):
        image = stream.read()

        cv.imshow('camera', image)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord(' '):
            print("Saving image ", snap_count)
            cv.imwrite("%s%d.png" % (file_name, snap_count), image)
            snap_count += 1

    cv.destroyAllWindows()
    stream.stop()


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
    args = parser.parse_args()

    snap(args.output_folder, args.width, args.height, args.count)

    print("Files saved")


if __name__ == "__main__":
    main()
