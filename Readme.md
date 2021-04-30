# Defeating Cyclops with Computer Vision
## About
This project aims to compete with cutting-edge machine vision calibration systems, delivering equivalent performance while utilising low-cost consumer hardware. Blackman & White is a company that produces state-of-the-art CNC cutting machines. A vital component of these machines is their outstanding cutting accuracy, which requires a robust calibration system to precisely align the cutting head with the material. The current system in use at Blackman & White is an expensive array of cameras that takes hours of manual work to calibrate. This project plans to solve these two problems using the most advanced techniques in computer vision. 

## Client Program
Contained in `cyclops/machine/`.
Can be run with `python main.py`.
It does not take any arguments.
When launched, it will start waiting for frames to be sent to it from the Pis. These frames will be displayed in a montage. The user can press "q" at any time to exit this stage of the program and proceed to stitch the images. Once stitching is finished, the program will write it to disk and display it in a window.

The setup program for calibration is called `setup_params.py`. It takes a filename to output the results to. It functions very similarly to `main.py` but saves the pamrameters instead of loading them.

## Pi Program
Contained in `cyclops/pi/`.
Can be run with `./main.py`.
It has the config filename as a required argument, and the `--preview` flag can be used to enable preview mode.

The config file is called `config.json` and can be edited by the user to change any parameters of the program without editing the code.

In normal mode, the program will listen for TCP messages or a GPIO to take an image. However, in preview mode, the TCP server is disabled and frames are streamed constantly to the client instead.

## Camera Calibration Scripts
Contained in `cyclops/calibration/`
`snap_interactive.py` used to take calibration images.
`calibrate.py` used to estimate camera instrinsics.

## Images
Contained in `cyclops/images/`
All the images used for testing the different algorithms are stored here.
