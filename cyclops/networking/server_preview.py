# import required libraries
from vidgear.gears import PiGear
from vidgear.gears import NetGear
import socket
import json

options = {
    "hflip": True,
    "exposure_mode": "auto",
    "iso": 800,
    "exposure_compensation": 15,
    "awb_mode": "horizon",
    "sensor_mode": 0,
}

# Open suitable video stream (webcam on first index in our case)
stream = PiGear(resolution=(640, 480), framerate=30,
                logging=True, **options).start()
# activate multiserver_mode
options = {"multiserver_mode": True}

# Define NetGear Server at Client's IP address and assign a unique port address and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
server = NetGear(
    address="100.86.213.15", port="5567", protocol="tcp", pattern=2, **options
)

camera_id = socket.gethostname()
frame_count, encoder_count = 0, 0
# loop over until Keyboard Interrupted
while True:
    try:
        # read frames from stream
        frame = stream.read()

        # check for frame if not None-type
        if frame is None:
            break
        frame_data = {
            "camera_id": camera_id,
            "frame_count": frame_count,
            "encoder_count": encoder_count
        }
        frame_data_json = json.dumps(frame_data)
        # send frame and frame data to client
        server.send(frame, message=frame_data_json)

        frame_count += 1

    except KeyboardInterrupt:
        break

# safely close video stream
stream.stop()

# safely close server
server.close()
