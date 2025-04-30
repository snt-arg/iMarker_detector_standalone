import cv2 as cv
import numpy as np
import dearpygui.dearpygui as dpg
from src.gui.utils import hsvToRgbHex, hsvToRgbTuple


def guiElements(cfg: dict, singleCamera: bool = False):
    """
    Defines GUI elements using Dear PyGui

    Parameters
    -------
    cfg: dict
        The dictionary containing the system parameters
    singleCamera: bool
        The bool to set the command of single/double camera setup
    """

    # Extract parameters
    cfgMode = cfg['mode']
    cfgAlgortihm = cfg['algorithm']
    cfgUsbCam = cfg['sensor']['usbCam']
    cfgSensor = cfg['sensor']['general']
    cfgProc = cfgAlgortihm['process']
    cfgColorRange = cfgProc['colorRange']
    greenRange = cfgColorRange['hsv_green']
    cfgPostproc = cfgAlgortihm['postprocess']
    thresholdSize = cfgPostproc['threshold']['size']
    thresholdMethod = cfgPostproc['threshold']['method']

    isRChannel = cfgProc['channel'] == 'r'
    isGChannel = cfgProc['channel'] == 'g'
    isBChannel = cfgProc['channel'] == 'b'
    isThreshAdapt = thresholdMethod == 'adaptive'
    isThreshBin = thresholdMethod == 'binary'

    isUsbCam = cfgMode['runner'] == 'usb'
    isRealSense = cfgMode['runner'] == 'rs'
    isSiViIR = cfgMode['runner'] == 'sv_ir'
    isOffImg = cfgMode['runner'] == 'offimg'
    isOffVid = cfgMode['runner'] == 'offvid'
    isSequential = cfgMode['temporalSubtraction']
    isUV = cfgMode['runner'] in ['offimguv', 'usbuv']

    # Color variables
    greenRangeLow = hsvToRgbTuple(greenRange['lower'])
    greenRangeHigh = hsvToRgbTuple(greenRange['upper'])

    # Window title
    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
    windowTitle = f"iMarker Readout - {'Single' if singleCamera else 'Double'} Vision Setup"
    if isOffImg or isOffVid or isRealSense:
        windowTitle += f" [{setupVariant}]"
    if isUV:
        windowTitle += " [UV Camera Mode]"

    with dpg.window(label=windowTitle, tag="MainWindow",
                    width=dpg.get_viewport_client_width(), height=dpg.get_viewport_client_height()):
        # Main Tabs
        with dpg.child_window(tag="Configs", autosize_x=True, height=150):
            with dpg.tab_bar():
                # General Settings
                with dpg.tab(label="General Settings"):
                    # Circular mask for old USB camera setup
                    if isUsbCam:
                        dpg.add_text(
                            f"Boosting frame-rate? {'Enabled' if cfgSensor['fpsBoost'] else 'Disabled'}")
                        with dpg.group(horizontal=True):
                            dpg.add_checkbox(
                                label="Enable circular mask", default_value=cfgUsbCam['enableMask'], tag="CircMaskEnable")
                            dpg.add_spacer(width=30)
                            dpg.add_slider_float(label="Circular mask radius size", default_value=cfgUsbCam['maskSize'],
                                                 width=200, min_value=0.0, max_value=1.0, tag="CircMask", format="%.2f")

                    if not isUV:
                        if (singleCamera and isSequential) or not singleCamera:
                            dpg.add_checkbox(label="Reverse subtraction order",
                                             default_value=cfgProc['subtractRL'], tag="SubtractionOrder")
                        with dpg.group(horizontal=True):
                            dpg.add_text("Color-range filter:")
                            dpg.add_radio_button(items=["Red", "Green", "Blue", "All"], tag="ColorChannel", horizontal=True,
                                                 default_value=("Red" if isRChannel else "Green" if isGChannel else "Blue" if isBChannel else "All"))

                    dpg.add_checkbox(label="Invert binary image",
                                     default_value=cfgPostproc['invertBinary'], tag="invertBinaryImage")

                    with dpg.group(horizontal=True):
                        dpg.add_slider_float(label="Brightness (Alpha)", min_value=0.1, max_value=5.0, width=200,
                                             default_value=cfgSensor['brightness']['alpha'], tag="camAlpha", format="%.1f")
                        dpg.add_spacer(width=50)
                        dpg.add_slider_int(label="Contrast (Beta)", min_value=0, max_value=50, width=200,
                                           default_value=cfgSensor['brightness']['beta'], tag="camBeta")

                if not isUV and singleCamera:
                    with dpg.tab(label="Color Range Picker"):
                        with dpg.group(horizontal=True):
                            # Low range Green
                            dpg.add_color_picker(
                                label="Green Low", tag="GreenRangeLow", width=100,
                                display_hsv=True, no_inputs=False, default_value=greenRangeLow)
                            dpg.add_spacer(width=50)
                            dpg.add_color_picker(
                                label="Green High", tag="GreenRangeHigh", width=100,
                                display_hsv=True, default_value=greenRangeHigh)

                if not singleCamera:
                    with dpg.tab(label="Alignment Configurations"):
                        dpg.add_slider_int(label="Max Features", min_value=10, max_value=1000, width=200,
                                           default_value=cfgProc['alignment']['maxFeatures'], tag="MaxFeat")
                        dpg.add_slider_float(label="Match Rate", min_value=0.0, max_value=1.0, width=200,
                                             default_value=cfgProc['alignment']['matchRate'], tag="MatchRate", format="%.2f")

                with dpg.tab(label="Post-Processing"):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Threshold Method:")
                        dpg.add_radio_button(items=["Adaptive", "Binary", "Otsu"], tag="ThreshMethod", horizontal=True,
                                             default_value=("Adaptive" if isThreshAdapt else "Binary" if isThreshBin else "Otsu"))
                    dpg.add_slider_int(label="Threshold Value", min_value=1, max_value=255, width=200,
                                       default_value=thresholdSize, tag="Threshold")
                    dpg.add_slider_int(label="Erosion Kernel Size", min_value=1, max_value=50, width=200,
                                       default_value=cfgPostproc['erosionKernel'], tag="Erosion")
                    dpg.add_slider_int(label="Gaussian Kernel Size", min_value=1, max_value=50, width=200,
                                       default_value=cfgPostproc['gaussianKernel'], tag="Gaussian")

        with dpg.child_window(tag="Viewers", autosize_x=True, height=-1):
            with dpg.tab_bar(tag="ImageTabBar"):
                if singleCamera:
                    if isUV:
                        with dpg.tab(label="Raw Frame", tag="RawFrameTab"):
                            dpg.add_image("FramesMain")
                        with dpg.tab(label="Mask Frame", tag="MaskFrameTab"):
                            dpg.add_image("FramesMask")
                        with dpg.tab(label="Mask Applied", tag="MaskAppliedTab"):
                            dpg.add_image("FramesMaskApplied")
                        with dpg.tab(label="Detected Markers", tag="MarkersTab"):
                            dpg.add_image("FramesMarker")
                    else:
                        if isSequential:
                            with dpg.tab(label="Previous Frame", tag="RawFrameLeftTab"):
                                dpg.add_image("FramesLeft")
                            with dpg.tab(label="Current Frame", tag="RawFrameRightTab"):
                                dpg.add_image("FramesRight")
                            with dpg.tab(label="Mask Frame", tag="MaskFrameTab"):
                                dpg.add_image("FramesMask")
                            with dpg.tab(label="Mask Applied", tag="MaskAppliedTab"):
                                dpg.add_image("FramesMaskApplied")
                            with dpg.tab(label="Detected Markers", tag="MarkersTab"):
                                dpg.add_image("FramesMarker")
                        else:
                            with dpg.tab(label="Raw Frame", tag="RawFrameTab"):
                                dpg.add_image("FramesMain")
                            with dpg.tab(label="Mask Frame", tag="MaskFrameTab"):
                                dpg.add_image("FramesMask")
                            with dpg.tab(label="Mask Applied", tag="MaskAppliedTab"):
                                dpg.add_image("FramesMaskApplied")
                            with dpg.tab(label="Detected Markers", tag="MarkersTab"):
                                dpg.add_image("FramesMarker")
                else:
                    with dpg.tab(label="Raw Frame Left", tag="RawFrameLeftTab"):
                        dpg.add_image("FramesLeft")
                    with dpg.tab(label="Raw Frame Right", tag="RawFrameRightTab"):
                        dpg.add_image("FramesRight")
                    with dpg.tab(label="Mask Frame", tag="MaskFrameTab"):
                        dpg.add_image("FramesMask")
                    with dpg.tab(label="Detected Markers", tag="MarkersTab"):
                        dpg.add_image("FramesMarker")

        # Footer
        with dpg.group(horizontal=True):
            dpg.add_image("LogoImage", width=30, height=28)
            dpg.add_text(
                "© 2022-2025 - TRANSCEND Project - University of Luxembourg")
            dpg.add_spacer(width=-1)
            dpg.add_button(label="Save the Current Frame", tag="Record",
                           callback=onRecord)


def updateWindowSize(sender, app_data):
    dpg.configure_item("MainWindow",
                       width=dpg.get_viewport_client_width(),
                       height=dpg.get_viewport_client_height())


def loadImageAsTexture(path: str, tag: str):
    """
    Loads an image from a file and creates a texture in DearPyGui

    Parameters
    -------
    path: str
        The path to the image file
    tag: str
        The tag to identify the texture in DearPyGui
    """
    # Read image using OpenCV (BGR)
    img = cv.imread(path, cv.IMREAD_UNCHANGED)

    # If grayscale, convert to BGRA
    if len(img.shape) == 2:
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGRA)
    elif img.shape[2] == 3:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGBA)
    elif img.shape[2] == 4:
        img = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)

    height, width, _ = img.shape
    # Normalize to 0–1 float
    img = img.astype(np.float32) / 255.0
    # Flatten row-major
    imgData = img.flatten()

    with dpg.texture_registry():
        dpg.add_static_texture(width, height, imgData, tag=tag)


def updateImageTexture(frame: np.ndarray, tag: str):
    """
    Converts an OpenCV BGR/BGRA image to RGBA float32 format and updates the DPG texture.

    Parameters
    ----------
    frame : np.ndarray
        The image to display (BGR or BGRA format).
    tag : str
        The texture tag to update (must be registered in dpg.texture_registry).
    """
    width, height = frame.shape[1], frame.shape[0]
    # Convert to RGBA
    if len(frame.shape) == 2:  # Grayscale
        frame = cv.cvtColor(frame, cv.COLOR_GRAY2RGBA)
    elif frame.shape[2] == 3:  # BGR
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
    elif frame.shape[2] == 4:  # BGRA
        frame = cv.cvtColor(frame, cv.COLOR_BGRA2RGBA)
    else:
        raise ValueError("Unsupported image format!")

    # Normalize to [0.0, 1.0]
    frame = frame.astype(np.float32) / 255.0

    # Make sure it's (H, W, 4)
    assert frame.shape[2] == 4, f"Expected 4 channels, got {frame.shape[2]}"

    # Convert to 1D list (flatten row-major)
    flat_frame = frame.astype(np.float32).reshape(-1).tolist()

    try:
        dpg.set_value(tag, flat_frame)
    except Exception as e:
        print(f"[ERROR] Failed to update texture: {e}")


def updateColorPreview(window, config):
    """
    Updates the color preview based on the HSV values

    Parameters
    -------
    window: Window
        The window containing all the GUI
    config: dict
        The dictionary containing various parameters
    """
    # Variables
    greenRange = config['hsv_green']

    # Update the GUI
    window['PreviewGreenRangeL'].update(
        background_color=hsvToRgbHex(greenRange['lower'][0] * 360 / 180,
                                     greenRange['lower'][1],
                                     greenRange['lower'][2]))
    window['PreviewGreenRangeH'].update(
        background_color=hsvToRgbHex(greenRange['upper'][0] * 360 / 180,
                                     greenRange['upper'][1],
                                     greenRange['upper'][2]))


def onRecord():
    """
    Callback function to handle the record button click event.
    """
    dpg.set_value("RecordFlag", True)


def onImageViewTabChange(imageDict):
    # Update the displayed images
    activeTabId = dpg.get_value("ImageTabBar")
    activeTabTag = dpg.get_item_alias(activeTabId)
    # Only update the image if the tab is changed
    if activeTabTag == "RawFrameLeftTab":
        updateImageTexture(imageDict['left'], 'FramesLeft')
    elif activeTabTag == "RawFrameRightTab":
        updateImageTexture(imageDict['right'], 'FramesRight')
    elif activeTabTag == "RawFrameTab":
        updateImageTexture(imageDict['main'], 'FramesMain')
    elif activeTabTag == "MaskFrameTab":
        updateImageTexture(imageDict['mask'], 'FramesMask')
    elif activeTabTag == "MaskAppliedTab":
        updateImageTexture(imageDict['maskApplied'], 'FramesMaskApplied')
    elif activeTabTag == "MarkersTab":
        updateImageTexture(imageDict['marker'], 'FramesMarker')
