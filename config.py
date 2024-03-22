import os
import cv2 as cv
import numpy as np

# GUI elements
labelSize = (20, 1)     # Setting label size in the GUI
inputSize = (30, 1)     # Setting input size in the GUI
sliderSize = (100, 15)  # Setting slider size in the GUI
windowWidth = 1800      # Max. shown window width
windowLocation = (0, 0)  # Window location

# Files
videoPath = "/home/ali/Videos/vid2.MOV"   # Path to the offline video file
imagesPath = "/home/ali/Pictures/img/"   # Path to the offline image file
imagesNames = ['Halide_RH_5m.jpg',
               'Halide_LH_5m.jpg']   # Names of the images

# Sensors
exposureTime = 20000
# Camera ports for USB sensors (0 for internal webcam)
ports = {'lCam': "/dev/video2", 'rCam': "/dev/video4"}
sensorProjectRoot = f"{os.getcwd()}/src/csr_sensors/sensors/config"
brightness = {'alpha': 1.0, 'beta': 0}  # Setting brightness of the cameras
realSenseFps = 30   # Frame-rate of the sensor, used for configuring RealSense
realSenseResolution = (640, 480)     # Resolution of the frames in RealSense

# CSR-based Marker
leftHanded = True   # If True, it is left-handed, otherwise, it is right-handed

# Pre-processing
fpsBoost = True         # Enabling fps boost for USB cameras
channel = 'g'       # Enabling RGB channels (options: all, r, g, b)
# Dimensions of ROI for iDS camera setup
roiDimension = {
    'cap1': {
        'x': 520,
        'y': 300,
        'width': 976,
        'height': 900
    },
    'cap2': {
        'x': 480,
        'y': 284,
        'width': 976,
        'height': 900
    },
}

# Processing
maxFeatures = 500               # Maximum number of features for alignment
goodMatchPercentage = 0.4
circlularMaskCoverage = 0.8     # Value between 0 and 1
flipImage = True                # True for BeamSplitter, False for stereo-vision
# True for inverting the black and white colors in the image
invertBinaryImage = True
enableCircularROI = False       # True for USB Setup, False for iDS
# Apply the homography matrix below to do alignment only once
preAligment = True
# In the single camera setup, whether to use sequential subtraction or just thresholding
isSequentialSubtraction = True
# Homography matrix for iDS cameras
# Structure: [[scaling x-axis, skewing x-axis, shift x-axis]
#             [skewing y-axis, scaling y-axis, shift y-axis]
#             [perspective x-axis, perspective y-axis, scaling all]]
homographyMatList = {
    'Settings1': np.array([[1.01621457e+00,  3.58445420e-02, -2.44065632e+01],
                          [-9.84581954e-03,  1.02765380e+00, -1.40367861e+01],
                          [4.41648502e-06,  3.15020103e-05,  1.00000000e+00]]),
    'Settings2': np.array([[1.00810034e+00, -8.35518266e-03,  8.24430129e+00],
                          [5.04865290e-03,  1.01568339e+00, -2.56132273e+00],
                          [-6.06091127e-06,  1.69549217e-05,  1.00000000e+00]]),
    'Settings3': np.array([[1.03330539e+00, -2.33383557e-02,  7.86579611e+00],
                           [2.72445070e-02,  1.01455844e+00, -1.21160907e+01],
                           [2.72468851e-05, -5.08436884e-06,  1.00000000e+00]]),
    'Settings4': np.array([[9.99409645e-01, -1.55228281e-02, -3.79768922e+00],
                           [1.65593615e-02,  1.00673047e+00, -4.11314756e+00],
                           [-9.96470609e-06, 1.68764309e-05,  1.00000000e+00]]),
    'Settings5': np.array([[1.01572100e+00, -1.51550480e-02, -9.08269647e+00],
                           [1.91107875e-02,  1.01081982e+00, -4.37920015e+00],
                           [-4.06011658e-06, 1.52890809e-05,  1.00000000e+00]])
}
homographyMat = homographyMatList['Settings4']

# Post-processing
# Thresholding method (options: both, binary, otsu)
thresholdMethod = 'binary'
# The value of threshold for separating layers (between 0 and 255)
threshold = 30
# The size of the kernel for erosion (between 1 and 50)
erodeKernelSize = 1
# The size of the kernel for gaussian blur (only odd values)
gaussianBlurKernelSize = 1

# Aruco Marker Detection
# Aruco dictionary to use for marker detection
arucoDict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_ORIGINAL)
# Aruco parameters to use for marker detection
arucoParams = cv.aruco.DetectorParameters()
# Aruco marker size in meters
arucoSize = 0.1
