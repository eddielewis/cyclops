import matplotlib.pyplot as plt
import numpy as np
import cv2
import json


from load_camera_matrix import camera_matrix, dist_coefs, rvecs, tvecs

ids = ["0", "1", "2", "3", "4", "5", "6", "7"]
transformations = [
    np.array((0.00, 0.00, 0.00)),
    np.array((0.05, 0.00, 0.00)),
    np.array((0.00, -0.05, 0.00)),
    np.array((0.05, -0.05, 0.00)),
    np.array((0.00, -0.10, 0.00)),
    np.array((0.05, -0.10, 0.00)),
    np.array((0.00, -0.15, 0.00)),
    np.array((0.05, -0.15, 0.00))
]


def compare(data_path):
    f = open(data_path, "r")
    data = f.read()
    obj = json.loads(data)
    for frame in obj.values():
        if all(id in frame for id in ids):
            rvecs0, tvecs0, obj_points0 = [
                np.array(x) for x in frame["0"].values()]
            for id in ids:
                rvecs, tvecs, obj_points = [
                    np.array(x) for x in frame[id].values()]
                image_points0, _ = cv2.projectPoints(
                    obj_points, rvecs, tvecs, camera_matrix, dist_coefs)
                for i in range(4):
                    obj_points[i] += transformations[int(id)]
                image_points1, _ = cv2.projectPoints(
                    obj_points, rvecs0, tvecs0, camera_matrix, dist_coefs)

                x, y = image_points0.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="b", label=str(id))

                x, y = image_points1.flatten("F").reshape(2, -1)
                plt.scatter(x, y, c="r", label=str(id))

            plt.ylim(0, 480)
            plt.xlim(0, 640)
            plt.gca().set_aspect('equal', adjustable='box')
            plt.legend(loc="upper left")
            plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Uses images from folder specified to calculate camera calibration matrix.")
    parser.add_argument("data_path",
                        help="Path to JSON file containing marker data.")
    args = parser.parse_args()

    compare(args.data_path)


if __name__ == "__main__":
    main()
