import json
from imutils.video import VideoStream
import numpy as np
import cv2
import cv2.aruco as aruco
import time
from load_camera_matrix import camera_matrix, dist_coefs

vs = VideoStream(usePiCamera=True, framerate=32, resolution=(
    640, 480), rotation=180).start()
time.sleep(2.0)

# MARKER_LENGTH = 0.011
MARKER_LENGTH = 0.02

frame_count = 0
aruco_markers = {}
while(True):
    frame = vs.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    arucoParameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=arucoParameters)
    frame = aruco.drawDetectedMarkers(frame, corners)

    # This function receives the detected markers and returns their pose estimation respect to the camera individually.
    # So for each marker, one rotation and translation vector is returned.
    # The returned transformation is the one that transforms points from each marker coordinate system to the camera coordinate system.
    # The marker corrdinate system is centered on the middle of the marker, with the Z axis perpendicular to the marker plane.
    # The coordinates of the four corners of the marker in its own coordinate system are:
    # (-markerLength/2, markerLength/2, 0), (markerLength/2, markerLength/2, 0),
    # (markerLength/2, -markerLength/2, 0), (-markerLength/2, -markerLength/2, 0)
    rvecs, tvecs, obj_points = aruco.estimatePoseSingleMarkers(
        corners, MARKER_LENGTH, camera_matrix, dist_coefs)
    if ids is not None:
        aruco_markers[frame_count] = {}
        for i in range(ids.size):
            print(i)
            aruco_markers[frame_count][i] = {
                "rvecs": rvecs[i].tolist(), "tvecs": tvecs[i].tolist(), "obj_points": obj_points.tolist()}
            frame = aruco.drawAxis(
                frame, camera_matrix, dist_coefs, rvecs[i], tvecs[i], MARKER_LENGTH)
    frame_count += 1

    cv2.imshow('Display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
vs.stop()
cv2.destroyAllWindows()

f = open("aruco_markers.json", "w")
f.write(json.dumps(aruco_markers))
f.close()
