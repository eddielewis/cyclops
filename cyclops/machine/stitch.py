import imutils
import argparse
import cv2
import numpy as np
from .setup_params import PX_DIST


class Stitcher:
    def set_params_from_file(self, fn):
        with np.load(fn, allow_pickle=True) as f:
            self.t_matrices = f["t_matrices"].tolist()
            self.camera_layout = f["camera_layout"].tolist()

    def set_params(self, t_matrices, camera_layout):
        self.h_matrices = t_matrices
        self.camera_layout = camera_layout

    def stitch_h(self, frame_dict):
        if self.t_matrices is None or self.camera_layout is None:
            return None

        imgs = []
        for cam_id, img in frame_dict.items():
            T = self.t_matrices[cam_id]
            img = cv2.warpPerspective(
                img, T, (img.shape[1], img.shape[0]))
            corrected_img = img[:PX_DIST, :PX_DIST]
            img.append(corrected_img)

        stitched_img = np.hstack(imgs)
        return stitched_img

    def stitch_v(self, imgs):
        if self.h_matrices is None or self.camera_layout is None:
            return None
        if self.t_matrices is None or self.camera_layout is None:
            return None
        return np.vstack(imgs)


CAMERA_LAYOUT = ["cyclops1.local", "cyclops0.local"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("left_img",
                        type=str)
    parser.add_argument("right_img",
                        type=str)
    args = parser.parse_args()

    left_img = cv2.imread(args.left_img)
    right_img = cv2.imread(args.right_img)
    left_img = imutils.resize(left_img, width=400)
    right_img = imutils.resize(right_img, width=400)

    frame_dict = {
        "cyclops0.local": left_img,
        "cyclops1.local": right_img
    }

    h_matrices = calc_h_matrices(frame_dict)
    stitcher = Stitcher()
    stitcher.set_params(h_matrices, CAMERA_LAYOUT)

    h_img = stitcher.stitch_h(frame_dict, False)
    cv2.imshow("h img", h_img)

    v_img = stitcher.stitch_v([right_img, left_img])
    cv2.imshow("v img", v_img)

    cv2.waitKey(0)


if __name__ == "__main__":
    main()
