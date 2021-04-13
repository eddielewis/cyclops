from RPi import GPIO
from time import sleep
import multiprocessing as mp
from camera import CameraServer
from gpio import GPIOHandler
from tcp_server import PiTCPServer, PiTCPHandler
import socketserver
import threading

clk = 4
dt = 14

snap_in = 23
snap_out = 22


cam_ser = CameraServer()
gpio = GPIOHandler(snap_in, snap_out, cam_ser)


HOST = "0.0.0.0"
PORT = 5005
PiTCPServer.allow_reuse_address = True
server = PiTCPServer(cam_ser, (HOST, PORT), PiTCPHandler)
""" p = threading.Thread(target=server.serve_forever())
p.start() """

while True:
    try:
        server.serve_forever()
        # while True:
        # sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        t = threading.Thread(target=server.shutdown())
        t.start()
        gpio.close()
        cam_ser.close()
        t.join()

""" with socketserver.TCPServer((HOST, PORT), TCPHandler) as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.socket.close()
        stream.stop()
        server_netgear.close() """


""" self.value = 0
self.state = '00'
self.direction = None
self.callback = callback
GPIO.setup(self.leftPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(self.rightPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(self.leftPin, GPIO.BOTH,
                      callback=self.transitionOccurred)
GPIO.add_event_detect(self.rightPin, GPIO.BOTH,
                      callback=self.transitionOccurred)

HOST = "0.0.0.0"
PORT = 5005

run_server():
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)
    try:
        server.serve_forever()
    except Exception:
        stream.close()
        server_netgear.close()

p = mp.Process(target=run_server())
p.start()
 """
