# GUI settings
fpsBoost = True
labelSize = (20, 1)
inputSize = (30, 1)
sliderSize = (100, 15)

# ROS connector settings
rosTopic = 'marker_process'
rosNodes = {'lCam': '/cameraL/image_view',
            'rCam': '/cameraR/image_view', 'init': 'csr_readout'}

# Shown window
windowWidth = 1800
# Camera ports (0 for internal webcam)
ports = {'lCam': "/dev/video2", 'rCam': "/dev/video4"}
# Values for the left and the right camera
brightness = {'alpha': 3.0, 'beta': 0}

# Marker properties
leftHanded = True  # If True, it is left-handed, otherwise, it is right-handed

# Read Images
channel = 'g'  # Enabling RGB channels (variations: all, r, g, b)

# Image alignment
maxFeatures = 500
goodMatchPercentage = 0.4
circlularMaskCoverage = 0.8  # Value between 0 and 1
flipImage = True  # True for BeamSplitter, False for stereo-vision
enableCircularROI = True  # True for BeamSplitter, False for stereo-vision

# Post-processing initialize values
threshold = 30  # Value between 0 and 255
erodeKernelSize = 3  # Value between 1 and 50
gaussianBlurKernelSize = 3  # Only odd values
# Thresholding method (variations: both, binary, otsu)
thresholdMethod = 'binary'
