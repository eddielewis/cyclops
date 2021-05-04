from stitch import Stitcher
import json
import socket
from vidgear.gears import NetGear
import numpy as np
from imutils import build_montages
import cv2


class App():
    def __init__(self):
        with np.load("/home/ed/University/ce301_lewis_edward_f/cyclops/params.npz", allow_pickle=True) as f:
            t_matrices = f["h_matrices"].tolist()
            camera_layout = f["camera_layout"].tolist()
            self.origin = f["origin"]
            self.m_per_px = float(f["m_per_px"])

        self.stitcher = Stitcher()
        self.stitcher.set_params(t_matrices, camera_layout)

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

    def run(self):
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
        cv2.destroyAllWindows()
        self.client.close()
        return frame_dicts


def main():
    app = App()
    frame_dicts = app.run()

    imgs = []
    for frame_d in frame_dicts:
        stitched_img = app.stitcher.stitch_h(
            frame_d)
        cv2.imshow("stitched", stitched_img)
        cv2.waitKey(0)
        imgs.append(stitched_img)

    final_img = app.stitcher.stitch_v(imgs)
    cv2.imwrite("final.png", final_img)
    cv2.imshow("final", final_img)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()
