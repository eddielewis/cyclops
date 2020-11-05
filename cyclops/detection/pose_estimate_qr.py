import cv2
import numpy as np
import glob

with np.load('../calibration/calibration_images3_output/matrix/matrix_00.npz') as f:
    camera_matrix, dist_coefs, _, _ = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]


def draw(img, corners, imgpts):
    # for corner in corners[0]:
    corner = tuple(corners[0][0].ravel())
    print(corner)

    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img


criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((4, 3), np.float32)
objp[:, :2] = np.mgrid[0:2, 0:2].T.reshape(-1, 2)

axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)
for fname in glob.glob('qr_images2/*'):
    print(fname)
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    qr_decoder = cv2.QRCodeDetector()

    retval, decoded_info, corners, straight_qrcode = qr_decoder.detectAndDecodeMulti(
        img)

    # print(retval)

    if retval == True:
        # corners2 = cv2.cornerSubPix(
        #     gray, corners, (11, 11), (-1, -1), criteria)

        # Find the rotation and translation vectors.
        retval, rvecs, tvecs, inliers = cv2.solvePnPRansac(
            objp, corners, camera_matrix, dist_coefs, cv2.SOLVEPNP_ITERATIVE)

        # project 3D points to image plane
        imgpts, jac = cv2.projectPoints(
            axis, rvecs, tvecs, camera_matrix, dist_coefs)

        print(corners)

        img = draw(img, corners, imgpts)
        cv2.imshow('img', img)
        k = cv2.waitKey(0) & 0xff
        if k == 's':
            cv2.imwrite(fname[:6]+'q.png', img)

cv2.destroyAllWindows()
