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


def detect(pre_process, preview):
    vs = VideoStream(usePiCamera=True, framerate=30, resolution=(
        640, 480), rotation=180).start()
    time.sleep(2.0)

    while True:
        frame = vs.read()
        # frame = imutils.resize(frame, width=270)
        if pre_process:
            detect_frame = pre_process(frame)
        else:
            detect_frame = frame
        barcodes = decode(detect_frame, symbols=[ZBarSymbol.QRCODE])

        for barcode in barcodes:
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)

            if preview:
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                print(text)

        cv2.imshow("Barcode Scanner", frame)

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()


def pre_process_opencv(frame):
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur_frame = cv2.GaussianBlur(grey_frame, (5, 5), 0)
    ret, detect_frame = cv2.threshold(
        blur_frame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return detect_frame


def pre_process_binarization(frame):
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    return binarization.nlbin(pil_img)


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
