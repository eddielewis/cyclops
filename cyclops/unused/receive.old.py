from send_multicast import send
import errno
from picamera import PiCamera
from picamera.array import PiRGBArray
import os
import argparse
import sys
import time
import cv2 as cv
import socket
from multiprocessing import Process, Pipe

# taken from w3resource.com
IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
PORT = 5005

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((IP, PORT))


HOSTNAME = socket.gethostname()
file_name = ""
snap_count = 0

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(1.0)

image = None
snap_count = 0


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


parent_conn, child_conn = Pipe()

snap = Process(target=snap, args=(
    child_conn, "jim/", 640, 480, 0, False)).start()

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)
    print(data[0:4])
    # parent_conn.send("snap")
    save()
    if data[0:4] == "snap":
        print("snap")
        # command, folder, width, height, snap_count=data.split(",")
        # snap.snap(foldern, width, height, snap_count)
