import time
import socket
import threading
from snap import Snap

# taken from w3resource.com
IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
PORT = 5005

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((IP, PORT))

snap = Snap((640, 480), 32, "jim/", 0)
camera_process = threading.Thread(
    target=snap.start_capture, args=(False,)).start()
time.sleep(2.0)


while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)
    if data == b"snap":
        snap.save()
