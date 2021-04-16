# import required libraries
from vidgear.gears import NetGear
import cv2


class Client:
    def __init__(self, address, port, protocol="tcp", pattern=1, receive_mode=True, options={}):
        self.client = NetGear(
            address=address,
            port=port,
            protocol=protocol,
            pattern=pattern,
            receive_mode=receive_mode,
            **options
        )
        self.frame = None

    def listen(self, queue):
        while True:
            try:
                # receive data from network
                data = self.client.recv()
                # check if data received isn't None
                if data is None:
                    break
                print("jim")
                # extract unique port address and its respective frame
                port, extracted_data, frame = data

                self.frame = frame
                queue.put(frame)

                # cv2.imshow("of", frame)
                # cv2.waitKey(1)

            except KeyboardInterrupt:
                break

    def close(self):
        self.client.close()

    def show(self):
        return self.frame
