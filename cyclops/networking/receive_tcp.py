import sys
import socket


# taken from w3resource.com, finds the ip of this Pi
IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
PORT = 5005


def main():

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_STREAM)  # TCP

    sock.bind((IP, PORT))
    sock.setblocking

    try:
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print("received message: %s" % data)
    except (KeyboardInterrupt, SystemExit):
        print("stopping")
        sys.exit()


if __name__ == "__main__":
    main()
