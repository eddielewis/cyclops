import errno
from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera.exc import PiCameraValueError
import sys
import time
import cv2 as cv
import os
import socket

class Snap():
    def __init__(self, resolution, framerate):
        # initialize the camera and grab a reference to the raw camera capture
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)

    def start_capture(self, preview):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            self.image = frame.array
            self.rawCapture.truncate(0)

        cv.destroyAllWindows()

    def get_frame(self):
        return self.image

    def stop(self):
        try:
            self.camera.close()
        except PiCameraValueError:
            pass
