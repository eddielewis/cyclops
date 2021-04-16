import socket


class Sender:
    def __init__(self, pi_hostnames, port):
        self.pi_ips = []
        for hostname in pi_hostnames:
            ip = socket.gethostbyname(hostname)
            self.pi_ips.append(ip)
        self.port = port

    def send(self, message):
        for ip in self.pi_ips:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, self.port))
            s.send(message)
            s.close()


def main():
    pi_hostnames = ["cyclops0.local", "cyclops1.local"]
    sender = Sender(pi_hostnames, 5005)
    sender.send(b"snap")


if __name__ == "__main__":
    main()
