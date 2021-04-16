
import socket


TCP_IP = "cyclops0.local"
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = b"Hello, World!"

""" s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(b"start_capture")
data = s.recv(BUFFER_SIZE)
s.close()
print("received data:", data) """

""" s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(b"snap")
data = s.recv(BUFFER_SIZE)
s.close()
print("received data:", data) """

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("cyclops1.local", TCP_PORT))
s.send(b"snap")
data = s.recv(BUFFER_SIZE)
s.close()
print("received data:", data)
