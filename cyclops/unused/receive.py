#!/home/pi/.virtualenvs/cv/bin/python3.7

import sys
import time
import socket
import threading
from snap import Snap
import json
import argparse


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# taken from w3resource.com, finds the ip of this Pi
IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
PORT = 5005


def save_snap():
    snap.save()


def close():
    raise SystemExit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("preview",
                        help="Enable preview of the camera",
                        default=False)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP

    sock.bind((IP, PORT))

    snap = Snap((640, 480), 32, "jim/", 0)
    camera_process = StoppableThread(
        target=snap.start_capture, args=(args.preview,))
    camera_process.daemon = True
    camera_process.start()
    time.sleep(2.0)

    try:
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received message: %s" % data)
            message = json.loads(data)
            globals()[message["command"]]()
    except (KeyboardInterrupt, SystemExit):
        camera_process.stop()
        snap.stop()
        print("stopping")
        sys.exit()


if __name__ == "__main__":
    main()
