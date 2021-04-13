from threading import Thread
import socketserver


multicast_group = ('224.3.29.71', 10000)


def __init__():
    receive = mp.Process(target=receive).start()


def save_image():


def setup_camera():


def setup_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(server_address)

    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq)


def receive():
    while True:
        data, address = sock.recvfrom(1024)

        print('received {} bytes from {}'.format(
            len(data), address))
        print(data[0:4])
        if data[0:4] == "snap":
            command, folder, width, height, snap_count = data.split(",")
            snap.snap(foldern, width, height, snap_count)

        print('sending acknowledgement to', address)
        sock.sendto(b'ack', address)


def send(message):
    # Set the time-to-live for messages to 1 so they do not
    # go past the local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # Send data to the multicast group
        print('sending {!r}'.format(message))
        sent = sock.sendto(message, multicast_group)

        # Look for responses from all recipients
        while True:
            print('waiting to receive')
            try:
                data, server = sock.recvfrom(16)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print('received {!r} from {}'.format(
                    data, server))

    finally:
        print('closing socket')
        sock.close()
