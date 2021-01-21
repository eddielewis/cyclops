import matplotlib.pyplot as plt
import numpy as np
import cv2
import json


with np.load('../../calibration/data/calibration_images3_output/matrix/matrix_00.npz') as f:
    camera_matrix, dist_coefs, camera_rvecs, camera_tvecs = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]

f = open("detection/compare3.json", "r")
data = f.read()
obj = json.loads(data)


for frame in obj.values():
    if "0" in frame and "1" in frame:
        rvecs0, tvecs0, obj_points0 = [
            np.array(x) for x in frame["0"].values()]
        rvecs1, tvecs1, obj_points1 = [
            np.array(x) for x in frame["1"].values()]

        image_points0, _ = cv2.projectPoints(
            obj_points0, rvecs0, tvecs0, camera_matrix, dist_coefs)
        image_points1, _ = cv2.projectPoints(
            obj_points1, rvecs1, tvecs1, camera_matrix, dist_coefs)

        v = np.array((0, 0.1, 0))
        for i in range(4):
            obj_points0[i] += v

        image_points2, _ = cv2.projectPoints(
            obj_points0, rvecs0, tvecs0, camera_matrix, dist_coefs)

        for points in [image_points0, image_points1, image_points2]:
            x, y = points.flatten("F").reshape(2, -1)
            plt.scatter(x, y)

        plt.ylim(0, 480)
        plt.xlim(0, 640)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
