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
        'y': 200,
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
    'Settings4': np.array([[1.05178314e+00,  7.47381640e-03, -6.00956602e+00],
                           [2.26952543e-02,  1.08586602e+00, -3.55523734e+01],
                           [1.19584372e-05,  5.47181939e-05,  1.00000000e+00]]),
    'Settings5': np.array([[1.00599877e+00, -1.48766070e-02,  9.61639584e+00],
                           [2.28028148e-02,  9.99854316e-01, -9.24323584e+00],
                           [1.20355482e-05, -1.35088334e-05,  1.00000000e+00]])
}
homographyMat = homographyMatList['Settings2']

# Post-processing
# Thresholding method (options: both, binary, otsu)
thresholdMethod = 'binary'
# The value of threshold for separating layers (between 0 and 255)
threshold = 30
# The size of the kernel for erosion (between 1 and 50)
erodeKernelSize = 3
# The size of the kernel for gaussian blur (only odd values)
gaussianBlurKernelSize = 3
