from imutils.video import VideoStream
import numpy as np
import cv2
import cv2.aruco as aruco
import time
# cap = cv2.VideoCapture(0)
vs = VideoStream(usePiCamera=True, framerate=32, resolution=(
    640, 480), rotation=180).start()
time.sleep(2.0)

MARKER_LENGTH = 0.011


with np.load('../calibration/calibration_images3_output/matrix/matrix_00.npz') as f:
    camera_matrix, dist_coefs, _, _ = [f[i] for i in (
        'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs')]

while(True):
    # ret, frame = cap.read()
    frame = vs.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    frame = aruco.drawDetectedMarkers(frame, corners)

    rvecs, tvecs, obj_points = aruco.estimatePoseSingleMarkers(
        corners, MARKER_LENGTH, camera_matrix, dist_coefs)
    if ids is not None:
        print(ids[0])
        for i in range(ids.size):
            frame = aruco.drawAxis(
                frame, camera_matrix, dist_coefs, rvecs[i], tvecs[i], MARKER_LENGTH)

    cv2.imshow('Display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
