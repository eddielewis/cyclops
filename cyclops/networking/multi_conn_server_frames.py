import socket
import selectors
import types
import struct
import cv2
import pickle


sel = selectors.DefaultSelector()

host = socket.gethostname()
port = 8089

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# data = b''  # CHANGED
payload_size = struct.calcsize("=L")  # CHANGED


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'', msg_size=None)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            if len(data.inb) < payload_size:
                data.inb += recv_data
            elif data.msg_size is None:
                packed_msg_size = data.inb[:payload_size]
                data.inb = data.inb[payload_size:]
                data.msg_size = struct.unpack(
                    "=L", packed_msg_size)[0]  # CHANGED
            elif len(data.inb) < data.msg_size:
                data.inb += recv_data
            else:
                frame_data = data.inb[:data.msg_size]
                data.inb = data.inb[data.msg_size:]
                print(type(frame_data))

                # Extract frame
                frame = pickle.loads(frame_data)

                # Display
                cv2.imshow('frame', frame)
                # cv2.imwrite("jim.png", frame)
                cv2.waitKey(1)
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()


while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

""" if recv_data:
    data.inb += recv_data
    # Retrieve message size
    while len(data.inb) < payload_size:
        data.inb += sock.recv(4096)
    packed_msg_size = data.inb[:payload_size]
    data.inb = data.inb[payload_size:]
    msg_size = struct.unpack("=L", packed_msg_size)[0]  # CHANGED

    # Retrieve all data based on message size
    while len(data.inb) < msg_size:
        data.inb += sock.recv(4096)

    frame_data = data.inb[:msg_size]
    data = data.inb[msg_size:]

    # Extract frame
    frame = pickle.loads(frame_data)

    # Display
    cv2.imshow('frame', frame)
    # cv2.imwrite("jim.png", frame)
    cv2.waitKey(1) """

""" recv_data = sock.recv(1024)  # Should be ready to read
if recv_data:
    data.outb += recv_data
else:
    print('closing connection to', data.addr)
    sel.unregister(sock)
    sock.close() """
""" if mask & selectors.EVENT_WRITE:
if data.outb:
    print('echoing', repr(data.outb), 'to', data.addr)
    sent = sock.send(data.outb)  # Should be ready to write
    data.outb = data.outb[sent:] """
