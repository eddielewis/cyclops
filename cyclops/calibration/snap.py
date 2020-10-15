"""
Saves a series of snapshots with the current camera as snapshot_<width>_<height>_<nnn>.jpg
Arguments:
    --f <output folder>     default: current folder
    --n <file name>         default: snapshot
    --w <width px>          default: none
    --h <height px>         default: none
Buttons:
    q           - quit
    space bar   - save the snapshot


"""

import cv2 as cv
import time
import sys
import argparse
import os
from imutils.video import VideoStream

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


def save_snaps(width=0, height=0, name="snapshot", folder="."):
    vs = VideoStream(usePiCamera=True, resolution=(
        1920, 1080), framerate=80).start()
    time.sleep(2.0)
    if width > 0 and height > 0:
        print("Setting the custom Width and Height")
        cap.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            # ----------- CREATE THE FOLDER -----------------
            folder = os.path.dirname(folder)
            try:
                os.stat(folder)
            except:
                os.mkdir(folder)
    except:
        pass

    nSnap = 0

    fileName = "%s/%s_%d_%d_" % (folder, name, CAMERA_WIDTH, CAMERA_HEIGHT)
    while(True):
        image = vs.read()

        cv.imshow('camera', image)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord(' '):
            print("Saving image ", nSnap)
            cv.imwrite("%s%d.jpg" % (fileName, nSnap), image)
            nSnap += 1

    cv.destroyAllWindows()
    vs.stop()


def main():
    SAVE_FOLDER = "."

    # ----------- PARSE THE INPUTS -----------------
    parser = argparse.ArgumentParser(
        description="Saves snapshot from the camera. \n q to quit \n spacebar to save the snapshot")
    parser.add_argument("--folder", default=SAVE_FOLDER,
                        help="Path to the save folder (default: current)")
    args = parser.parse_args()

    SAVE_FOLDER = args.folder

    save_snaps(folder=args.folder)

    print("Files saved")


if __name__ == "__main__":
    main()
