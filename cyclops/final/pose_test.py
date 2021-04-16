import argparse
import numpy as np
import cv2
import cv2.aruco as aruco
# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("img_path",
                    type=str,
                    help="Path to the image")
args = parser.parse_args()

img = cv2.imread(args.img_path)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
arucoParameters = aruco.DetectorParameters_create()
arucoParameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
corners, ids, rejectedImgPoints = aruco.detectMarkers(
    gray, aruco_dict, parameters=arucoParameters)


def calc_median(py_list):
    py_list.sort()
    i = len(py_list) // 2
    # if length is even
    if len(py_list) % 2 == 0:
        # average two middle values
        return (py_list[i-1] + py_list[i]) / 2
    else:
        return py_list[i]


def calc_mm_per_px(marker_side_len_m, marker_corners):
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


def pt_px_to_world(pt, origin, mm_per_px):
    return (pt - origin) * mm_per_px


m_per_px = calc_mm_per_px(corners, 0.0195)
print(m_per_px)
origin = corners[0][0, 0]
print("origin:", origin)
pts = []
for i in range(3):
    c = corners[i][0]
    print(c[0])
    p = [pt_px_to_world(c, origin, mm_per_px) for c in corners[i][0]]
    print(p)
