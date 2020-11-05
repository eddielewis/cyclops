# import the necessary packages
from imutils.video import VideoStream
from pyzbar.pyzbar import decode, ZBarSymbol
import argparse
import datetime
import imutils
import time
import cv2
from kraken import binarization
from PIL import Image
import multiprocessing as mp
import time
import numpy as np


frames_to_process = mp.Queue()

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6*9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)


def detect(pre_process, preview):
    capture = mp.Process(target=capture_video).start()
    process_video1 = mp.Process(target=process_frame).start()
    process_video2 = mp.Process(target=process_frame).start()
    process_video3 = mp.Process(target=process_frame).start()


def capture_video():
    vs = VideoStream(usePiCamera=True, framerate=32, resolution=(
        1280, 640), rotation=180).start()
    time.sleep(2.0)

    # start = time.perf_counter()
    while True:
        frame = vs.read()
        frames_to_process.put(frame)

        cv2.imshow("Detect OpenCV", frame)
        time.sleep(0.1)

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()


def process_frame():
    qr_decoder = cv2.QRCodeDetector()
    while True:
        start = time.perf_counter()
        print("Processing: %d" % frames_to_process.qsize())
        frame = frames_to_process.get()
        retval, decoded_info, points, straight_qrcode = qr_decoder.detectAndDecodeMulti(
            frame)
        for info in decoded_info:
            print("Decoded data: %s" % info)

        # if len(decoded_info) > 0:
        #     for data in decoded_info:
        #             print("Decoded Data : {}".format(data))
        #         # frame = display(frame, data)
        #         print(points[0])
        #         for rect in points:
        #             # box = np.int0(cv2.boxPoints(rect))
        #             # box = np.int0(points)
        #             cv2.drawContours(
        #                 frame, [rect.astype(int)], -1, (0, 255, 0), 3)
        #         # straight_qrcode = np.uint8(straight_qrcode)
        #         # cv2.imshow("Rectified QRCode", rectifiedImage)

        finish = time.perf_counter()
        processing_time = finish-start
        print("Frame processed in: %f" % processing_time)


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


def main():
    parser = argparse.ArgumentParser(
        description="Detects QR codes in video stream")
    parser.add_argument("--method",
                        help="Which method to use to try to improve detection.",
                        default=0,
                        type=int)
    parser.add_argument("-p",
                        help="Enables preview of camera.",
                        action="store_true"
                        )
    args = parser.parse_args()

    pre_process = None
    if args.method == 1:
        pre_process = pre_process_opencv
    elif args.method == 2:
        pre_process = pre_process_binarization

    detect(pre_process, args.p)


if __name__ == "__main__":
    main()
