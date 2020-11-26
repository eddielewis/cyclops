import errno
from picamera import PiCamera
from picamera.array import PiRGBArray
import sys
import time
import cv2 as cv
import os
import socket


class Snap():
    def __init__(self, resolution, framerate, folder, snap_count):
        # initialize the camera and grab a reference to the raw camera capture
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.image = None
        self.snap_count = 0
        self.setup(resolution, folder)

    def setup(self, resolution, folder):
        hostname = socket.gethostname()
        width, height = resolution
        try:
            os.makedirs(folder)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        self.file_name = "%s/%s_%d_%d_" % (folder, hostname,
                                           width, height)

    def start_capture(self, preview):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            self.image = frame.array

            if preview:
                cv.imshow('camera', self.image)

            self.rawCapture.truncate(0)

        cv.destroyAllWindows()
        vs.stop()

    def save(self):
        print("Saving image ", self.snap_count)
        cv.imwrite("%s%d.jpg" % (self.file_name, self.snap_count), self.image)
        self.snap_count += 1
