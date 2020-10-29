


# Test
## QR Code
Size 20mm
File code_40_4_3.png

## Monitor
Brightness 0
Contrast 20

## Detection
Resized to 400px
640x480 ~120mm
1280x720 ~160mm
1920x1080 ~220mm

Detection works best when the code and camera are coplanar, which is a bit difficult at the moment with current setup.

# Test 2
## QR Code 
Size 20mm

## Detection
Resized to 400px
640x480 90mm
Resized to 270px
1920x1080 90mm

# Test 3
## Method 1
Used OpenCV methods cvtColor(), GaussianBlur() and threshold() to try to improve detection though it does not seem to work much better than no-pre-processing.

# Test 4
## Method 2
Used cvtColor() and binaraization() from kranken library to imrpove detection. This method was very effective, though the framerate does suffer quite heavily. This might be imrpoved wit the use of threading so a consistent recording framerate can be achieved.

## QR Code
Size 20mm

## Detection
640x480 ~200mm