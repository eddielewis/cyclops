import cv2
import cv2.aruco as aruco
import numpy as np
from vidgear.gears import PiGear
from load_camera_matrix import camera_matrix, dist_coefs


"""

I think I've got it now. The problem was with the method described in step 4. The camera position cannot be calculated from the homography matrix alone. The camera intrinsics matrix is also necessary. So, the correct procedure is the following:

1) draw a map of the area

2) calibrate the camera using the chessboard image with cv2.findChessboardCorners this yields the camera matrix and the distortion coefficients

3) solvePnP with the world coordinates (3D) and image coordinates (2D). The solvePnP returns the object's origo in the camera's coordinate system given the 4 corresponding points and the camera matrix.

4) Now I need to calculate the camera's position in world coordinates. The rotation matrix is: rotM = cv2.Rodrigues(rvec)[0]

5) The x,y,z position of the camera is: cameraPosition = -np.matrix(rotM).T * np.matrix(tvec)

 """

options = {
    "hflip": True,
    "exposure_mode": "auto",
    "iso": 800,
    "exposure_compensation": 15,
    "awb_mode": "horizon",
    "sensor_mode": 0,
}

stream = PiGear(resolution=(640, 480), framerate=60,
                logging=True, **options).start()

aruco_parameters = aruco.DetectorParameters_create()
marker_length = 0.02

# TODO output frame wit axes drawn on?


def pose_estimate(camera_matrix, dist_coefs, marker_length, frame, aruco_parameters):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=aruco_parameters)
    # This function receives the detected markers and returns their pose estimation respect to the camera individually.
    # So for each marker, one rotation and translation vector is returned.
    # The returned transformation is the one that transforms points from each marker coordinate system to the camera coordinate system.
    # The marker corrdinate system is centered on the middle of the marker, with the Z axis perpendicular to the marker plane.
    # The coordinates of the four corners of the marker in its own coordinate system are:
    # (-markerLength/2, markerLength/2, 0), (markerLength/2, markerLength/2, 0),
    # (markerLength/2, -markerLength/2, 0), (-markerLength/2, -markerLength/2, 0)
    rvecs, tvecs, obj_points = aruco.estimatePoseSingleMarkers(
        corners, marker_length, camera_matrix, dist_coefs)
    # rvecs, tvecs and obj_points are np arrays
    # index of id in ids corresponds to items in rvecs and tvecs
    return ids, rvecs, tvecs, obj_points


def pose_estimate_camera(rvec, tvec):
    # retval, rvec, tvec = cv2.solvePnP(obj_points, imagePoints, cameraMatrix, distCoeffs[, rvec[, tvec[, useExtrinsicGuess[, flags]]]])
    rotM = cv2.Rodrigues(rvec)[0]
    camera_position = -np.matrix(rotM).T * np.matrix(tvec)
    print(camera_position)


while True:

    try:
        # read frames from stream
        frame = stream.read()

        # check for frame if not None-type
        if frame is None:
            break
        ids, rvecs, tvecs, obj_points = pose_estimate(
            camera_matrix, dist_coefs, marker_length, frame, aruco_parameters)
        cv2.imshow(frame)
        cv2.waitKey()
    except KeyboardInterrupt:
        break

# safely close video stream
stream.stop()
