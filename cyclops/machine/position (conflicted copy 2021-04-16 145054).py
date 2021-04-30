import argparse
import json
import cv2
import cv2.aruco as aruco
import numpy as np


class Position:
    def __init__(self, fn):
        with np.load(fn, allow_pickle=True) as f:
            self.origin = f["origin"]
            self.m_per_px = f["m_per_px"]
        """ self.origin = np.array([0, 0])
        self.m_per_px = 1.78 """

    def px_to_world(self, pt):
        return pt[0] - self.origin[0] * self.m_per_px, pt[1]-self.origin[1] * self.m_per_px


def find_markers(img):
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
    arucoParameters = aruco.DetectorParameters_create()
    arucoParameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        img, aruco_dict, parameters=arucoParameters)
    print("markers dected: ", len(ids))
    return ids, corners


def calc_median(py_list):
    if len(py_list) < 2:
        return None
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


def marker_centre(corners):
    x, y = 0, 0
    # corners = corners[0]
    print("ghgg corn", corners)
    for i in range(len(corners)):
        print(corners[i])
        x += corners[i][0, 0]
        print("ccccc", corners[i][0, 0])
        y += corners[i][0, 1]
    print(x, y)
    x /= 4
    y /= 4
    return x, y


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("img",
                        type=str)
    parser.add_argument("params_fn",
                        type=str)
    args = parser.parse_args()

    img = cv2.imread(args.img)

    """ with np.load(args.params_fn, allow_pickle=True) as f:
        origin = f["origin"]
        m_per_px = f["m_per_px"] """

    ids, corners = find_markers(img)

    data = {}
    position = Position(args.params_fn)
    position.origin = marker_centre(corners[0])
    corners = corners[0][0]
    for i in range(ids.size):
        print(corners[i])
        centre_px = marker_centre(corners[i])
        print(centre_px)
        centre_w = position.px_to_world(centre_px)
        print(centre_w)
        data[i] = centre_w

    # with open('markers.json', 'w') as f:
        # json.dump(data, f)


if __name__ == "__main__":
    main()
