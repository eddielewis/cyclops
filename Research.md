# Defeating Cyclops with QR Codes

## Outline

*"At present most machines are like Cyclops and have only one eye. This makes the process of them searching for  registration markers and material boundaries painfully slow. The goal of this project is to develop a multi-camera array to give binocular or  better vision to our machines. You might consider using the machine learning embedded [www.jevois.org](http://www.jevois.org) camera’s to recognise and triangulate QR codes in 3d space so as to align the cameras."*



## Resources

[OpenCV - Camera Calibration](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html#calibration)

[OpenCV - Epipolar Geometry](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_epipolar_geometry/py_epipolar_geometry.html)



## Things to think about

What resolution and frame rate will be required? Bearing in mind that the head can move up to 2000 mm per second. 

What height will the cameras be mounted at above the cutting be? This will probably affect the resolution required.

Ensuring all the cameras are synced up will be difficult, would it possible to stop the head momentarily instead? 

Does it require a video stream, or will pictures suffice? This would be important for performance.



## JeVois Camera

[JeVois Camera - QR Code Detection and Decoding](http://jevois.org/moddoc/DemoQRcode/modinfo.html)

The camera has a small processor and capability to run a QR code detection and decoding algorithm. 

### Cost

The camera itself is $50, with multiple kits including it ranging from $60 to $200. I think the configuration required for this project will be about $80 for each camera.

Shipping is an additional $22 on the order.



### Requirements

1 x USB 3.0 or 2 x USB 2.0

"For optimal performance, the JeVois-A33 smart camera requires  connection to at least two USB 2.0 ports, or at least one USB 3.0 ports. This is because the maximum power needed by JeVois-A33 is 3.5 Watts,  while a single USB 2.0 port can deliver a maximum of 2.5 Watts, and a  USB 3.0 port can deliver up to 4.5 Watts." - [source](https://www.jevoisinc.com/products/mini-usb-y-cable-2-5-feet-80cm-long)

If using this camera, considerations will have to made about whether the host device has the sufficient number of ports for the cameras. Processing power of the host device will also have to be investigated to determine how many cameras can be connected to it.

A Raspberry Pi 3, for example, has 2 x USB 3.0 and 2 x USB 2.0 so it could run 3 cameras. 

A powered USB hub could help with this.



### Performance

"You should be able to sustain 30 frames/s with camera resolution  320x240, and 15 frames/s with camera resolution 640x480 when running  this [QR code detection and decoding] module inside the JeVois smart camera." - [source](https://www.jevoisinc.com/collections/jevois-hardware/products/jevois-a33-smart-camera-beginner-turnkey-kit?variant=38827654090)



![https://cdn.shopify.com/s/files/1/1719/3183/files/comparison-to-rpi_1024x1024.png?v=1488568740](https://cdn.shopify.com/s/files/1/1719/3183/files/comparison-to-rpi_1024x1024.png?v=1488568740)



## Raspberry Pi Camera

[Camera](https://thepihut.com/products/raspberry-pi-camera-module)

[Pi](https://thepihut.com/products/raspberry-pi-4-model-b)





