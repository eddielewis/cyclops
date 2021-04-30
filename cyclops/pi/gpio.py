import pigpio


class GPIOHandler:

    """Class to decode mechanical rotary encoder pulses."""

    def __init__(self, gpio, camera_server):
        """
        Instantiate the class with the pi and gpios connected to
        rotary encoder contacts A and B.  The common contact
        should be connected to ground.  The callback is
        called when the rotary encoder is turned.  It takes
        one parameter which is +1 for clockwise and -1 for
        counterclockwise.

        EXAMPLE

        import time
        import pigpio

        import rotary_encoder

        pos = 0

        def callback(way):

           global pos

           pos += way

           print("pos={}".format(pos))

        pi = pigpio.pi()

        decoder = rotary_encoder.decoder(pi, 7, 8, callback)

        time.sleep(300)

        decoder.cancel()

        pi.stop()

        """
        self.camera_server = camera_server
        self.pi = pigpio.pi()
        # Setup the pins numbers passed to the constructor
        self.encoder0 = gpio.encoder0
        self.encoder1 = gpio.encoder1
        self.snap_in = gpio.snap_in
        self.snap_out = gpio.snap_out

        self.levA = 0
        self.levB = 0

        self.lastGpio = None

        # Set pin type: input or output
        self.pi.set_mode(self.encoder0, pigpio.INPUT)
        self.pi.set_mode(self.encoder1, pigpio.INPUT)
        self.pi.set_mode(self.snap_in, pigpio.INPUT)
        self.pi.set_mode(self.snap_out, pigpio.OUTPUT)
        # Sets whether to pull the input up or down with a 10K resistor
        self.pi.set_pull_up_down(self.encoder0, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.encoder1, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.snap_in, pigpio.PUD_DOWN)

        # Instantiates the callbacks which trigger on GPIO pin voltage rising or falling
        self.encoder0_cb = self.pi.callback(
            self.encoder0, pigpio.EITHER_EDGE, self._pulse)
        self.encoder1_cb = self.pi.callback(
            self.encoder1, pigpio.EITHER_EDGE, self._pulse)
        self.snap_cb = self.pi.callback(
            self.snap_in, pigpio.EITHER_EDGE, self.snap_read)

        self.pos = 0

    # Sends a signal to Pis to take an image
    def snap_trigger(self):
        self.pi.gpio_trigger(self.snap_out, 10, 1)
        self.camera_server.snap()

    # Receives the signal from to take an image
    def snap_read(self, gpio, level, tick):
        if level == 1:
            self.camera_server.snap()

    # Handles the rotation of the encoder
    def _pulse(self, gpio, level, tick):
        """
        Decode the rotary encoder pulse.

                     +---------+         +---------+      0
                     |         |         |         |
           A         |         |         |         |
                     |         |         |         |
           +---------+         +---------+         +----- 1

               +---------+         +---------+            0
               |         |         |         |
           B   |         |         |         |
               |         |         |         |
           ----+         +---------+         +---------+  1
        """

        if gpio == self.encoder0:
            self.levA = level
        else:
            self.levB = level

        if gpio != self.lastGpio:  # debounce
            self.lastGpio = gpio

            if gpio == self.encoder0:
                if level == 1:
                    if self.levB == 1:
                        self.pos += 1
                    else:
                        self.pos -= 1
                else:  # level == 0:
                    if self.levB == 0:
                        self.pos += 1

                    else:
                        self.pos -= 1
            else:  # gpio == self.encoder1
                if level == 1:
                    if self.levA == 1:
                        self.pos -= 1
                    else:
                        self.pos += 1

                else:  # level == 0:
                    if self.levA == 0:
                        self.pos -= 1
                    else:
                        self.pos += 1

            # Takes an image on even count of the encoder
            if self.pos % 2 == 0:
                self.snap_trigger()

    # Removes the event listeners on the GPIO pins
    def close(self):
        self.encoder0_cb.cancel()
        self.encoder1_cb.cancel()
        self.snap_cb.cancel()
