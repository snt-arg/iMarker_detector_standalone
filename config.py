import os
import numpy as np

# GUI elements
labelSize = (20, 1)     # Setting label size in the GUI
inputSize = (30, 1)     # Setting input size in the GUI
sliderSize = (100, 15)  # Setting slider size in the GUI
windowWidth = 1800      # Shown window width
windowLocation = (800, 400)     # Window location

# Sensors
exposureTime = 20000
# Camera ports for USB sensors (0 for internal webcam)
ports = {'lCam': "/dev/video2", 'rCam': "/dev/video4"}
sensorProjectRoot = f"{os.getcwd()}/src/csr_sensors/sensors/config"
brightness = {'alpha': 3.0, 'beta': 0}  # Setting brightness of the cameras

# CSR-based Marker
leftHanded = True   # If True, it is left-handed, otherwise, it is right-handed

# Pre-processing
fpsBoost = True         # Enabling fps boost for USB cameras
channel = 'g'       # Enabling RGB channels (options: all, r, g, b)
# Dimensions of ROI for iDS camera setup
roiDimension = {
    'cap1': {
        'x': 528,
        'y': 212,
        'width': 976,
        'height': 1094
    },
    'cap2': {
        'x': 480,
        'y': 212,
        'width': 976,
        'height': 1094
    },
}

# Processing
maxFeatures = 500               # Maximum number of features for alignment
goodMatchPercentage = 0.4
circlularMaskCoverage = 0.8     # Value between 0 and 1
flipImage = True                # True for BeamSplitter, False for stereo-vision
enableCircularROI = False       # True for USB Setup, False for iDS
# Apply the homography matrix below to do alignment only once
preAligment = True
# Homography matrix for iDS cameras
homographyMat = np.array([[1.01621457e+00,  3.58445420e-02, -2.44065632e+01],
                          [-9.84581954e-03,  1.02765380e+00, -1.40367861e+01],
                          [4.41648502e-06,  3.15020103e-05,  1.00000000e+00]])

# Post-processing
# Thresholding method (options: both, binary, otsu)
thresholdMethod = 'binary'
# The value of threshold for separating layers (between 0 and 255)
threshold = 30
# The size of the kernel for erosion (between 1 and 50)
erodeKernelSize = 3
# The size of the kernel for gaussian blur (only odd values)
gaussianBlurKernelSize = 3
