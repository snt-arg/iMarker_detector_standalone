# ⚙️ Configuration Parameters

You can find below various configurations of the framework, which can be modified in [`config.yml`](/config/config.yaml):

| Main Category | Sub-Category  | Options                 | Description                                                 |
| ------------- | ------------- | ----------------------- | ----------------------------------------------------------- |
| `mode`        | -             | `runner`                | ["offimg", "offvid", "usb", "ids", "rs"]                    |
| `mode`        | -             | `sequentialSubtraction` | use sequential frame subtraction ("rs", "offimg", "offvid") |
| `gui`         | -             | `windowWidth`           | the width of the window in pixels                           |
| `gui`         | -             | `labelSize`             | the size of the label (e.g., [30, 1])                       |
| `gui`         | -             | `inputSize`             | the size of the input (e.g., [30, 1])                       |
| `gui`         | -             | `buttonSize`            | the size of the button (e.g., [30, 1])                      |
| `gui`         | -             | `sliderSize`            | the size of the slider (e.g., [30, 1])                      |
| `gui`         | -             | `windowLocation`        | the location of the window                                  |
| `gui`         | -             | `maxImageHolderSize`    | the maximum width of the image holder in pixels             |
| `sensor`      | `general`     | `fpsBoost`              | enable boosting frame-rate (for "usb")                      |
| `sensor`      | `general`     | `brightness`            | the brightness of the input (`alpha` and `beta`)            |
| `sensor`      | `offline`     | `image`                 | the `folder` with images titled `names` ["x.jpg", "y.jpg"]  |
| `sensor`      | `offline`     | `video`                 | the `path` of video titled (e.g., "x.mov")                  |
| `sensor`      | `offline`     | `video` -> `rotate`     | enable rotating the video                                   |
| `sensor`      | `usbCam`      | `maskSize`              | the mask size designed to filter unmatched outputs          |
| `sensor`      | `usbCam`      | `flipImage`             | enable flipping the second camera's image                   |
| `sensor`      | `usbCam`      | `enableMask`            | enable the circular mask for filtration                     |
| `sensor`      | `usbCam`      | `ports`                 | ports `lCam` and `rCam` of the USB cameras                  |
| `sensor`      | `ids`         | `exposureTime`          | the exposure time of iDS cameras                            |
| `sensor`      | `ids`         | `roi`                   | the Region of Interest (ROI) of iDS cameras                 |
| `sensor`      | `realSense`   | `fps`                   | the frame-rate of the camera                                |
| `sensor`      | `realSense`   | `resolution`            | the resolution of the camera in `width` and `height`        |
| `algorithm`   | `process`     | `matchRate`             | the matching rate of images in dual-vision ("usb" "ids")    |
| `algorithm`   | `process`     | `usePreset`             | using a calibrated homography matrix instead of matching    |
| `algorithm`   | `process`     | `maxFeatures`           | maximum number of features for matching                     |
| `algorithm`   | `process`     | `channel`               | the channel to focus on ["b", "g", "r", "all"]              |
| `algorithm`   | `process`     | `subtractRL`            | left-to-right or right-to-left subtraction                  |
| `algorithm`   | `postprocess` | `threshold`             | threshold `size` and `method` (["binary", "otsu", "both"])  |
| `algorithm`   | `postprocess` | `invertBinary`          | inverting the binary image                                  |
| `algorithm`   | `postprocess` | `erosionKernelSize`     | erosion kernel size                                         |
| `algorithm`   | `postprocess` | `gaussianKernelSize`    | gaussian kernel size                                        |
| `marker`      | `structure`   | `size`                  | the size of the marker                                      |
| `marker`      | `detection`   | `dictionary`            | the dictionary of the marker (e.g., "DICT_ARUCO_ORIGINAL")  |
