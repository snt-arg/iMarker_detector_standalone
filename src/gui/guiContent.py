import cv2 as cv
import numpy as np
import dearpygui.dearpygui as dpg
from src.gui.utils import hsvToRgbHex


def guiElements(cfg: dict, imageSize: tuple, singleCamera: bool = False):
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
    cfgGui = cfg['gui']
    cfgMode = cfg['mode']
    cfgAlgortihm = cfg['algorithm']
    cfgUsbCam = cfg['sensor']['usbCam']
    cfgSensor = cfg['sensor']['general']
    cfgProc = cfgAlgortihm['process']
    cfgColorRange = cfgProc['colorRange']
    cfgPostproc = cfgAlgortihm['postprocess']
    thresholdSize = cfgPostproc['threshold']['size']
    thresholdMethod = cfgPostproc['threshold']['method']
    greenRange = cfgColorRange['hsv_green']
    greenLHue = greenRange['lower'][0]
    greenUHue = greenRange['upper'][0]
    greenLSat = greenRange['lower'][1]
    greenUSat = greenRange['upper'][1]

    isRChannel = cfgProc['channel'] == 'r'
    isGChannel = cfgProc['channel'] == 'g'
    isBChannel = cfgProc['channel'] == 'b'
    isAllChannels = cfgProc['channel'] == 'all'
    isThreshOts = thresholdMethod == 'otsu'
    isThreshAdapt = thresholdMethod == 'adaptive'
    isThreshBin = thresholdMethod == 'binary'

    isUsbCam = cfgMode['runner'] == 'usb'
    isRealSense = cfgMode['runner'] == 'rs'
    isOffImg = cfgMode['runner'] == 'offimg'
    isOffVid = cfgMode['runner'] == 'offvid'
    isSequential = cfgMode['sequentialSubtraction']
    isUV = cfgMode['runner'] in ['offimguv', 'usbuv']

    # Window title
    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
    windowTitle = f"iMarker Readout - {'Single' if singleCamera else 'Double'} Vision Setup"
    if isOffImg or isOffVid or isRealSense:
        windowTitle += f" [{setupVariant}]"
    if isUV:
        windowTitle += " [UV Camera Mode]"

    # Load logo image
    loadImageAsTexture("./src/logo.png", "LogoImage")

    # Define textures
    height, width = imageSize[:2]
    with dpg.texture_registry(show=True):
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMain")

    # GUI content
    with dpg.window(label=windowTitle, tag="MainWindow",
                    width=dpg.get_viewport_client_width(), height=dpg.get_viewport_client_height()):
        # Main Tabs
        with dpg.child_window(tag="Configs", autosize_x=True, height=200):
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
                        dpg.add_checkbox(label="Reverse subtraction order",
                                         default_value=cfgProc['subtractRL'], tag="SubtractionOrder")
                        with dpg.group(horizontal=True):
                            dpg.add_text("Color-range filter:")
                            dpg.add_radio_button(items=["Red", "Green", "Blue", "All"], tag="ColorChannel", horizontal=True,
                                                 default_value=("Red" if isRChannel else "Green" if isGChannel else "Blue" if isBChannel else "All"))

                    dpg.add_checkbox(label="Invert binary image",
                                     default_value=cfgPostproc['invertBinary'], tag="invertBinaryImage")

                    with dpg.group(horizontal=True):
                        dpg.add_slider_float(label="Brightness (Alpha)", min_value=1.0, max_value=15.0, width=200,
                                             default_value=cfgSensor['brightness']['alpha'], tag="camAlpha", format="%.1f")
                        dpg.add_spacer(width=50)
                        dpg.add_slider_int(label="Contrast (Beta)", min_value=0, max_value=50, width=200,
                                           default_value=cfgSensor['brightness']['beta'], tag="camBeta")

                if not isUV and singleCamera:
                    with dpg.tab(label="Color Range Picker"):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Green Low (Hue/Sat):")
                            dpg.add_spacer(width=50)
                            dpg.add_slider_int(label="Hue Low", min_value=35, max_value=60, width=200,
                                               default_value=greenLHue, tag="GreenRangeHueLow")
                            dpg.add_spacer(width=50)
                            dpg.add_slider_int(label="Sat Low", min_value=10, max_value=255, width=200,
                                               default_value=greenLSat, tag="GreenRangeSatLow")

                        with dpg.group(horizontal=True):
                            dpg.add_text("Green High (Hue/Sat):")
                            dpg.add_spacer(width=50)
                            dpg.add_slider_int(label="Hue High", min_value=61, max_value=80, width=200,
                                               default_value=greenUHue, tag="GreenRangeHueHigh")
                            dpg.add_spacer(width=50)
                            dpg.add_slider_int(label="Sat High", min_value=10, max_value=255, width=200,
                                               default_value=greenUSat, tag="GreenRangeSatHigh")

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
                                       default_value=cfgPostproc['erosionKernelSize'], tag="Erosion")
                    dpg.add_slider_int(label="Gaussian Kernel Size", min_value=1, max_value=49, width=200,
                                       default_value=cfgPostproc['gaussianKernelSize'], tag="Gaussian")

        with dpg.child_window(tag="Viewers", autosize_x=True, height=-1):
            with dpg.tab_bar():
                if singleCamera:
                    if isSequential:
                        with dpg.tab(label="Previous Frame"):
                            dpg.add_text("PreviousFrame")
                            # dpg.add_image("FramesLeft")
                        with dpg.tab(label="Current Frame"):
                            dpg.add_text("CurrentFrame")
                            # dpg.add_image("FramesRight")
                        with dpg.tab(label="Mask Frame"):
                            dpg.add_text("MaskFrame")
                            # dpg.add_image("FramesMask")
                        with dpg.tab(label="Mask Applied"):
                            dpg.add_text("MaskApplied")
                            # dpg.add_image("FramesMaskApplied")
                        with dpg.tab(label="Detected Markers"):
                            dpg.add_text("DetectedMarkers")
                            # dpg.add_image("FramesMarker")
                    else:
                        with dpg.tab(label="Raw Frame"):
                            dpg.add_image("FramesMain")
                        with dpg.tab(label="Mask Frame"):
                            dpg.add_text("MaskFrame")
                            # dpg.add_image("FramesMask")
                        with dpg.tab(label="Mask Applied"):
                            dpg.add_text("MaskApplied")
                            # dpg.add_image("FramesMaskApplied")
                        with dpg.tab(label="Detected Markers"):
                            dpg.add_text("DetectedMarkers")
                            # dpg.add_image("FramesMarker")
                else:
                    with dpg.tab(label="Raw Frame Left"):
                        dpg.add_text("RawFrameL")
                        # dpg.add_image("FramesLeft")
                    with dpg.tab(label="Raw Frame Right"):
                        dpg.add_text("RawFrameR")
                        # dpg.add_image("FramesRight")
                    with dpg.tab(label="Mask Frame"):
                        dpg.add_text("MaskFrame")
                        # dpg.add_image("FramesMaskApplied")
                    with dpg.tab(label="Detected Markers"):
                        dpg.add_text("DetectedMarkers")
                        # dpg.add_image("FramesMarker")

        # Footer
        with dpg.group(horizontal=True):
            dpg.add_image("LogoImage", width=30, height=28)
            dpg.add_text(
                "© 2022-2025 - TRANSCEND Project - University of Luxembourg")
            dpg.add_spacer(width=-1)
            dpg.add_button(label="Save the Current Frame", tag="Record")


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


def getGUI(config: dict, singleCamera: bool = False, imageSize: tuple = None,
           postInitImages: list = None):
    """
    Creates a set of GUI elements using DearPyGui and returns the window ID

    Parameters
    -------
    config: dict
        The dictionary containing various parameters
    singleCamera: bool
        The bool to set the command of single/double camera setup
    imageSize: tuple
        The size of the image to be displayed in the GUI
    postInitImages: list
        The list of images to be displayed after the GUI is initialized
    """
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()
    dpg.set_viewport_resize_callback(updateWindowSize)
    guiElements(config, imageSize, singleCamera)

    # Register a render callback (executed after GUI is ready)
    if postInitImages:
        def updateAfterGui():
            for img, tag in postInitImages:
                updateImageTexture(img, tag)
        dpg.set_frame_callback(1, updateAfterGui)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def checkTerminateGUI():
    """
    Creates a set of GUI elements and send it back

    Returns
    -------
    guiShouldStop: bool
        The bool to set the command of stop/continue GUI
    """
    return not dpg.is_viewport_ok()


def getGUIValue(tag: str):
    """
    Returns the value of a GUI element

    Parameters
    -------
    tag: str
        The tag of the GUI element

    Returns
    -------
    value: any
        The value of the GUI element
    """
    return dpg.get_value(tag)


def renderFrame():
    """
    Renders the DearPyGui frame
    """
    dpg.render_dearpygui_frame()


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
