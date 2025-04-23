"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

import os
import cv2 as cv
import numpy as np
import dearpygui.dearpygui as dpg
from .gui.utils import frameSave, resizeFrame
from .utils import startProfiler, stopProfiler
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame
from .csr_sensors.sensors.config.cameraPresets import cameraMatrix_RealSense, distCoeffs_RealSense
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


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
    isSequential = cfgMode['temporalSubtraction']
    isUV = cfgMode['runner'] in ['offimguv', 'usbuv']

    # Window title
    singleCamera = True
    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
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
        frame1RawFetched, cfgGui['imageHolderWidth'])
    frame2RawFetched = resizeFrame(
        frame2RawFetched, cfgGui['imageHolderWidth'])

    # Initialize the GUI
    dpg.create_context()
    dpg.create_viewport(title='iMarker Detector Software')
    dpg.setup_dearpygui()
    dpg.set_viewport_resize_callback(updateWindowSize)

    # Load logo image
    loadImageAsTexture("./src/logo.png", "LogoImage")

    # Use an invisible container for internal values
    with dpg.value_registry():
        dpg.add_bool_value(default_value=False, tag="RecordFlag")

    # Register a render callback (executed after GUI is ready)
    postInitImages = [(frame1RawFetched, 'FramesMask'),
                      (frame1RawFetched, 'FramesMaskApplied'),
                      (frame1RawFetched, 'FramesMarker'),
                      (frame1RawFetched, 'FramesLeft'),
                      (frame1RawFetched, 'FramesRight'),
                      (frame1RawFetched, 'FramesMain')]

    def updateAfterGui():
        for img, tag in postInitImages:
            updateImageTexture(img, tag)
    dpg.set_frame_callback(1, updateAfterGui)

    # Define textures
    height, width = frame1RawFetched.shape[:2]
    with dpg.texture_registry(show=True):
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesLeft")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesRight")
        dpg.add_dynamic_texture(width, height, default_value=[
            0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMain")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMask")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMaskApplied")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMarker")

    # GUI content
    guiElements(config, singleCamera)

    dpg.show_viewport()

    # Loop
    while dpg.is_dearpygui_running():
        # Get GUI values
        alpha = dpg.get_value('camAlpha')
        beta = dpg.get_value('camBeta')

        # Re-write the config values based on the GUI changes
        config['algorithm']['process']['subtractRL'] = dpg.get_value(
            'SubtractionOrder')
        config['algorithm']['postprocess']['erosionKernel'] = dpg.get_value(
            'Erosion')
        config['algorithm']['postprocess']['gaussianKernel'] = dpg.get_value(
            'Gaussian') if dpg.get_value('Gaussian') % 2 == 1 else dpg.get_value('Gaussian') + 1
        config['algorithm']['postprocess']['threshold']['size'] = dpg.get_value(
            'Threshold')
        config['algorithm']['postprocess']['invertBinary'] = dpg.get_value(
            'invertBinaryImage')
        config['algorithm']['process']['colorRange']['hsv_green']['lower'][0] = int(
            dpg.get_value('GreenRangeHueLow'))
        config['algorithm']['process']['colorRange']['hsv_green']['lower'][1] = int(
            dpg.get_value('GreenRangeSatLow'))
        config['algorithm']['process']['colorRange']['hsv_green']['upper'][0] = int(
            dpg.get_value('GreenRangeHueHigh'))
        config['algorithm']['process']['colorRange']['hsv_green']['upper'][1] = int(
            dpg.get_value('GreenRangeSatHigh'))
        # Thresholding value
        config['algorithm']['postprocess']['threshold']['method'] = dpg.get_value(
            'ThreshMethod').lower()
        # Channel selection
        colorChannelValue = dpg.get_value('ColorChannel')
        channel = 'r' if colorChannelValue == 'Red' else 'g' if dpg.get_value(
            'ColorChannel') == 'Green' else 'b' if colorChannelValue == 'Blue' else 'All'
        config['algorithm']['process']['channel'] = channel

        frame1Raw = frame1RawFetched.copy()
        frame2Raw = frame2RawFetched.copy()

        # Change brightness
        frame1Raw = cv.convertScaleAbs(frame1Raw, alpha=alpha, beta=beta)
        frame2Raw = cv.convertScaleAbs(frame2Raw, alpha=alpha, beta=beta)

        if (isSequential):
            # Process the frames
            pFrame, cFrame, frameMask = processSequentialFrames(
                frame1Raw, frame2Raw, True, config)
            # Apply the mask
            frameMaskApplied = cv.bitwise_and(
                cFrame, cFrame, mask=frameMask)
        else:
            # Keep the original frame
            cFrameRGB = np.copy(frame2Raw)
            # Process the frames
            cFrame, frameMask = processSingleFrame(
                frame2Raw, True, config)
            frameMaskApplied = cv.bitwise_and(
                cFrame, cFrame, mask=frameMask)

        # Convert to RGB
        frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

        # Camera parameters
        distCoeffs = distCoeffs_RealSense
        cameraMatrix = cameraMatrix_RealSense

        # ArUco marker detection
        frameMarkers = arucoMarkerDetector(
            frameMask, cameraMatrix, distCoeffs, cfgMarker['detection']['dictionary'],
            cfgMarker['structure']['size'])

        # Update the textures
        onImageViewTabChange({
            'left': frame1Raw,
            'right': frame2Raw,
            'main': frame2Raw,
            'mask': frameMask,
            'maskApplied': frameMaskApplied,
            'marker': frameMarkers
        })

        # Record the frame(s)
        if dpg.get_value("RecordFlag"):
            imageList = [frame1Raw, frame2Raw, frameMarkers] if (
                cfgMode['temporalSubtraction']) else [frame2Raw, frameMarkers]
            concatedImage = imageConcatHorizontal(imageList, 1800)
            frameSave(concatedImage, cfgMode['runner'])
            dpg.set_value("RecordFlag", False)

        # You can manually stop by using stop_dearpygui()
        dpg.render_dearpygui_frame()

    print(
        f'Framework stopped! [Offline Images Captured by Single Vision Setup - {setupVariant}]')
    cv.destroyAllWindows()
    dpg.destroy_context()
