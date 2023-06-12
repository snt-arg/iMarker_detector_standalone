# CSR Detector Standalone (with GUI)

![Demo](docs/demo.png "Demo")

This repository contains the standalone version of **CSR-based object detector** which provides a Graphical User Interface (GUI) for easier usage of the codes. Accordingly, the application is dependant to the repositories below:

- CSR Sensors ([link](https://github.com/snt-arg/csr_sensors)): contains the sensors supported by the application.
- CSR Detector ([link](https://github.com/snt-arg/csr_detector)): contains the detector algorithm to filter CSR-based materials.

## 📚 Preparation

### I. Cloning

When cloning the repository include `--recurse-submodules` after `git clone` such that the submodules are added as well. Accordingly, you can use the command below:

```
git clone --recurse-submodules git@github.com:snt-arg/csr_detector_standalone.git
```

You can also get the latest changes of each submodule individually using the command `git pull --recurse-submodules`.

### II. Installing Python Libraries

Install the required libraries for running this program using the command below:

```
pip install numpy opencv-python PySimpleGUI
```

### III. Installing Submodule Packages

The next step is to intall the cloned submodules and define dependencies and other distribution-related configurations using the provided `setup.py` file in the root directory. Then, run `pip install -e .` in the **root directory** to install the package and its dependencies. You can also run the same command in the submodules directories to install them.

### 🚀 Running the Code

For running the code, there are three different modules, each designed based on the demands of a particular sensor.

| File | Description  |
| ------------ | ------------ |
| `mainIDS.py` | Running the GUI-enabled code with iDS camera sensors |
| `mainUSB.py` | Running the GUI-enabled code with USB camera sensors |
| `mainRS.py` | Running the GUI-enabled code with RealSense Monocular camera sensor |

There are also some configurations in the [config.py](config.py) file, as described below:

*GUI elements*
- `labelSize`: label size in the GUI, like (20, 1)
- `inputSize`: input size in the GUI, like (30, 1)
- `sliderSize`: slider size in the GUI, like (100, 15)
- `windowWidth`: what should be the size of the GUI
- `windowLocation`: where should the window appear

*Sensors*
- `exposureTime`: camera exposure time for iDS cameras, like 20000
- `ports`: camera ports for USB cameras, including left and right cameras
- `sensorProjectRoot`: the absolute location of the `Sensors` submodule for accessing its calibration files
- `brightness`: brightness value of the cameras, including `alpha` and `beta` values

*Markers*
- `leftHanded`: if the marker is left-handed or right-handed

*Pre-processing*
- `fpsBoost`: boosting fps of camera, mainly for the USB camera setup
- `channel`: enabling RGB channels (options: all, r, g, b)
- `roiDimension`: dimensions of ROI for iDS camera setup

*Processing*
- `maxFeatures`: maximum number of features for alignment, like 500
- `goodMatchPercentage`: percentage of a good match of features for alignment, like 0.4
- `circlularMaskCoverage`: how much the coverage of the circular mask should be (for the old design), like 0.8
- `flipImage`: should the images be flipped
- `enableCircularROI`: disable or enable the circular mask for USB cameras
- `preAligment`: apply the homography matrix below to do alignment only once
- `homographyMat`: a pre-defined homography matrix for iDS cameras

*Pos-processing*
- `thresholdMethod`: thresholding method (options: both, binary, otsu)
- `threshold`: the value of threshold for separating layers (between 0 and 255)
- `erodeKernelSize`: the size of the kernel for erosion (between 1 and 50)
- `gaussianBlurKernelSize`: the size of the kernel for gaussian blur (only odd values)