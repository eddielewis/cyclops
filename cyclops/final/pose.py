import numpy as np
import cv2.aruco as aruco
import argparse


def calc_median(py_list):
    py_list.sort()
    i = len(py_list) // 2
    # if length is even
    if len(py_list) % 2 == 0:
        # average two middle values
        return (py_list[i-1] + py_list[i]) / 2
    else:
        return py_list[i]


def calc_m_per_px(marker_corners, marker_side_len_m):
    side_l = []
    for i in range(len(marker_corners)):
        c = marker_corners[i][0]
        l = []
        l.append(np.linalg.norm(c[0]-c[1]))
        l.append(np.linalg.norm(c[1]-c[2]))
        l.append(np.linalg.norm(c[2]-c[3]))
        l.append(np.linalg.norm(c[3]-c[0]))
        med_l = calc_median(l)
        side_l.append(med_l)

    marker_side_len_px = calc_median(side_l)
    return marker_side_len_m / marker_side_len_px


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("img_path",
                        type=str,
                        help="Path to the image")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
