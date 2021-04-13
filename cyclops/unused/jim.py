from RPi import GPIO
from time import sleep

snap_in = 23
snap_out = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(snap_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(snap_out, GPIO.OUT)

counter = 0

try:

    while True:
        in_state = GPIO.input(snap_in)
        print(in_state)
        sleep(0.1)
finally:
    GPIO.cleanup()
