from RPi import GPIO


class GPIOHandler:
    def __init__(self, in_pin, out_pin, camera_server):
        GPIO.setmode(GPIO.BCM)
        self.in_pin = in_pin
        GPIO.setup(self.in_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.in_pin, GPIO.BOTH,
                              callback=self.read_pin)
        self.out_pin = out_pin
        GPIO.setup(self.out_pin, GPIO.OUT)
        self.camera_server = camera_server

    def read_pin(self, channel):
        print("esfoihfseo")
        p = GPIO.input(self.in_pin)
        print(p)
        if p:
            self.camera_server.snap()

    def pulse(self):
        GPIO.output(self.out_pin, GPIO.HIGH)
        sleep(0.1)
        GPIO.output(self.out_pin, GPIO.LOW)

    def close(self):
        GPIO.cleanup()
