from stitch import Stitcher
import threading
import json
import socket
from vidgear.gears import NetGear
import argparse
import numpy as np
import os
from imutils import build_montages
import cv2


class App():

    def __init__(self):
        with np.load("/home/ed/University/ce301_lewis_edward_f/cyclops/params.npz", allow_pickle=True) as f:
            h_matrices = f["h_matrices"].tolist()
            camera_layout = f["camera_layout"].tolist()
            self.origin = f["origin"]
            self.m_per_px = float(f["m_per_px"])

        self.stitcher = Stitcher()
        self.stitcher.set_params(h_matrices, camera_layout)

        options = {"multiserver_mode": True}
        ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
            ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        self.client = NetGear(
            address=ip,
            port=(5566, 5567),
            protocol="tcp",
            pattern=2,
            receive_mode=True,
            **options
        )

    def run(self, preview):
        frame_dicts = []
        while True:
            try:
                data = self.client.recv()
                if data is None:
                    break
                port, extracted_data, frame = data
                data = json.loads(extracted_data)
                camera_id = data["camera_id"]
                frame_count = data["frame_count"]
                if len(frame_dicts) > 3:
                    break
                try:
                    frame_dicts[frame_count][camera_id] = frame
                except IndexError:
                    frame_dicts.append({camera_id: frame})

                cv2.imshow("frame", frame)

                # if preview:
                (h, w) = frame.shape[:2]
                montages = build_montages(
                    frame_dicts[frame_count].values(), (w, h), (2, 1))
                for (i, montage) in enumerate(montages):
                    cv2.imshow("Montage Footage {}".format(i), montage)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            except KeyboardInterrupt:
                break

        # close output window
        cv2.destroyAllWindows()

        # safely close client
        self.client.close()
        return frame_dicts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", nargs="?", type=bool,
                        default=False, const=True)
    parser.add_argument("--estimate_H", nargs="?", type=bool,
                        default=False, const=True)
    args = parser.parse_args()

    app = App()
    frame_dicts = app.run(args.preview)

    imgs = []
    for frame_d in frame_dicts:
        stitched_img = app.stitcher.stitch_h(
            frame_d, estimate_H=args.estimate_h)
        cv2.imshow("stitched", stitched_img)
        cv2.waitKey(0)
        imgs.append(stitched_img)

    final_img = app.stitcher.stitch_v(imgs)
    cv2.imwrite("final.png", final_img)
    cv2.imshow("final", final_img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
