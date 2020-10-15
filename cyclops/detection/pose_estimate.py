import cv2 as cv
import numpy as np
import glob

with np.load('matrix.npz') as f:
    camera_matrix, dist_coefs, _, _ = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6*9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)

for fname in glob.glob('calibration_images3/*1*.jpg'):
    print(fname)
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, (9, 6), None)

    if ret == True:
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        retval, rvecs, tvecs, inliers = cv.solvePnPRansac(
            objp, corners2, camera_matrix, dist_coefs)

        # project 3D points to image plane
        imgpts, jac = cv.projectPoints(
            axis, rvecs, tvecs, camera_matrix, dist_coefs)

        print(imgpts)
        print(jac)

        img = draw(img, corners2, imgpts)
        cv.imshow('img', img)
        k = cv.waitKey(0) & 0xff
        if k == 's':
            cv.imwrite(fname[:6]+'q.png', img)

cv.destroyAllWindows()
