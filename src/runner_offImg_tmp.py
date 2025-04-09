import os
import cv2 as cv
import dearpygui.dearpygui as dpg
from .gui.utils import resizeFrame
from src.gui.guiContent import loadImageAsTexture, updateImageTexture, updateWindowSize


def runner_offImg(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']
    cfgAlgortihm = config['algorithm']
    cfgUsbCam = config['sensor']['usbCam']
    cfgSensor = config['sensor']['general']
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
    singleCamera = True
    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
    windowTitle = f"iMarker Readout - {'Single' if singleCamera else 'Double'} Vision Setup"
    if isOffImg or isOffVid or isRealSense:
        windowTitle += f" [{setupVariant}]"
    if isUV:
        windowTitle += " [UV Camera Mode]"

    setupVariant = "Sequential Subtraction" if cfgMode['sequentialSubtraction'] else "Masking"
    print(
        f'Framework started! [Offline Images Captured by Single Vision Setup - {setupVariant}]')

    # Check if the images files exist
    image1Path = os.path.join(
        cfgOffline['image']['folder'], cfgOffline['image']['names'][0])
    image2Path = os.path.join(
        cfgOffline['image']['folder'], cfgOffline['image']['names'][1])
    if not os.path.exists(image1Path) or not os.path.exists(image2Path):
        print("At leaset one image does not exist! Exiting ...")
        return

    # Variables
    frameMask = None
    frameMaskApplied = None

    # Open the image files
    frame1RawFetched = cv.imread(image1Path)
    frame2RawFetched = cv.imread(image2Path)

    # Resize frames if necessary
    frame1RawFetched = resizeFrame(
        frame1RawFetched, cfgGui['maxImageHolderSize'])
    frame2RawFetched = resizeFrame(
        frame2RawFetched, cfgGui['maxImageHolderSize'])

    # Initialize the GUI
    dpg.create_context()
    dpg.create_viewport(title='iMarker Detector Software')
    dpg.setup_dearpygui()
    dpg.set_viewport_resize_callback(updateWindowSize)

    # Load logo image
    loadImageAsTexture("./src/logo.png", "LogoImage")

    # Register a render callback (executed after GUI is ready)
    postInitImages = [(frame1RawFetched, 'FramesMain')]

    def updateAfterGui():
        for img, tag in postInitImages:
            updateImageTexture(img, tag)
    dpg.set_frame_callback(1, updateAfterGui)

    # Define textures
    height, width = frame1RawFetched.shape[:2]
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
                        dpg.add_slider_float(label="Brightness (Alpha)", min_value=0.1, max_value=5.0, width=200,
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

    dpg.show_viewport()

    # Loop
    while dpg.is_dearpygui_running():
        # Get GUI values
        alpha = dpg.get_value('camAlpha')
        beta = dpg.get_value('camBeta')

        frame1Raw = frame1RawFetched.copy()
        frame2Raw = frame2RawFetched.copy()

        # Change brightness
        frame1Raw = cv.convertScaleAbs(frame1Raw, alpha=alpha, beta=beta)
        frame2Raw = cv.convertScaleAbs(frame2Raw, alpha=alpha, beta=beta)

        # Update the displayed image
        updateImageTexture(frame1Raw, 'FramesMain')

        # You can manually stop by using stop_dearpygui()
        dpg.render_dearpygui_frame()

    print(
        f'Framework stopped! [Offline Images Captured by Single Vision Setup - {setupVariant}]')
    cv.destroyAllWindows()
    dpg.destroy_context()
