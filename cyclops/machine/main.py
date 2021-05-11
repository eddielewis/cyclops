from stitch import Stitcher
import json
import socket
from vidgear.gears import NetGear
import numpy as np
from imutils import build_montages
import cv2


class App():
    def __init__(self):
        # Loads parameters used for image stitching
        with np.load("/home/ed/University/ce301_lewis_edward_f/cyclops/machine/test.npz", allow_pickle=True) as f:
            t_matrices = f["t_matrices"].tolist()
            camera_layout = f["camera_layout"].tolist()
        # Sets up stitcher with parameters
        self.stitcher = Stitcher()
        self.stitcher.set_params(t_matrices, camera_layout)

        # Resolves this computer's IP
        # Taken from w3resources.com
        ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
            ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        # Starts NetGear client to receive frames from the Pis
        options = {"multiserver_mode": True}
        self.client = NetGear(
            address=ip,
            port=(5566, 5567),
            protocol="tcp",
            pattern=2,
            receive_mode=True,
            **options
        )

    def run(self):
        frame_dicts = []
        while True:
            try:
                # Waits on the next message received
                data = self.client.recv()
                if data is None:
                    break
                # Extract the data from the message
                port, extracted_data, frame = data
                data = json.loads(extracted_data)
                camera_id = data["camera_id"]
                frame_count = data["frame_count"]
                # Add the frame to the dict, if the dict doesn't exist, create it
                try:
                    frame_dicts[frame_count][camera_id] = frame
                except IndexError:
                    frame_dicts.append({camera_id: frame})
                # Create a montage of the frames recieved from each Pi
                (h, w) = frame.shape[:2]
                montages = build_montages(
                    frame_dicts[frame_count].values(), (w, h), (2, 1))
                for (i, montage) in enumerate(montages):
                    cv2.imshow("Montage Footage {}".format(i), montage)
                # Exits the function when q is pressed
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            except KeyboardInterrupt:
                break
        # Frees up resources used
        cv2.destroyAllWindows()
        self.client.close()
        return frame_dicts


def main():
    app = App()
    frame_dicts = app.run()

    imgs = []
    frame_dicts = frame_dicts[:-1]
    # Creates a horizontally stitched image for each set
    for frame_d in frame_dicts:
        print(frame_d.keys())
        stitched_img = app.stitcher.stitch_h(
            frame_d)
        cv2.imshow("stitched", stitched_img)
        cv2.waitKey(0)
        imgs.append(stitched_img)
    # Stitches the horizontal images vertically
    final_img = app.stitcher.stitch_v(imgs)
    cv2.imwrite("final.png", final_img)
    cv2.imshow("final", final_img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
