# import required libraries
from vidgear.gears import NetGear
from imutils import build_montages
import cv2
import socket
import json

# activate multiserver_mode
options = {"multiserver_mode": True}

# Define NetGear Client at given IP address and assign list/tuple
# of all unique Server((5566,5567) in our case) and other parameters
# !!! change following IP address '192.168.x.xxx' with yours !!!
ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]if not ip.startswith("127.")][:1], [[(s.connect(
    ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
client = NetGear(
    address=ip,
    port=(5566, 5567),
    protocol="tcp",
    pattern=1,
    receive_mode=True,
    **options
)

# Define received frame dictionary
frame_dict = {}

# loop over until Keyboard Interrupted
while True:

    try:
        # receive data from network
        data = client.recv()

        # check if data received isn't None
        if data is None:
            break

        # extract unique port address and its respective frame
        unique_address, extracted_data, frame = data

        print(extracted_data)

        # {do something with the extracted frame here}
        frame_data = json.loads(extracted_data)
        camera_id, frame_count, encoder_count = frame_data.values()
        cv2.imwrite("tmp/%s_%d_%d.png" %
                    (camera_id, frame_count, encoder_count), frame)

        # get extracted frame's shape
        (h, w) = frame.shape[:2]

        # update the extracted frame in the received frame dictionary
        frame_dict[unique_address] = frame

        # build a montage using data dictionary
        montages = build_montages(frame_dict.values(), (w, h), (2, 1))

        # display the montage(s) on the screen
        for (i, montage) in enumerate(montages):

            cv2.imshow("Montage Footage {}".format(i), montage)

        # check for 'q' key if pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    except KeyboardInterrupt:
        break

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()
