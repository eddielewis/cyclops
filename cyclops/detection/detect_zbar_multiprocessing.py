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
processed_frames = mp.Queue()

with np.load('../calibration/calibration_images3_output/matrix/matrix_00.npz') as f:
    camera_matrix, dist_coefs, _, _ = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


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

    while True:
        frame = vs.read()
        frames_to_process.put(frame)

        cv2.imshow("Detect Zbar", frame)
        time.sleep(0.1)

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()


def pre_process_binarization(frame):
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return binarization.nlbin(pil_img)


def process_frame():
    while True:
        start = time.perf_counter()
        print("Processing: %d" % frames_to_process.qsize())
        frame = frames_to_process.get()
        detect_frame = pre_process_binarization(frame)

        barcodes = decode(detect_frame, symbols=[ZBarSymbol.QRCODE])

        for barcode in barcodes:
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)

            retval, rvecs, tvecs, inliers = cv2.solvePnPRansac(
                objp, barcode.rect, camera_matrix, dist_coefs)

            imgpts, jac = cv2.projectPoints(
                axis, rvecs, tvecs, camera_matrix, dist_coefs)

            # if preview:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # else:
            # print(text)

        finish = time.perf_counter()
        processing_time = finish-start
        print("Frame processed in: %f" % processing_time)


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
