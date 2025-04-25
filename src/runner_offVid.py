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
from .gui.utils import resizeFrame, frameSave
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .iMarker_algorithms.vision.concatImages import concatFramesHorizontal
from .iMarker_algorithms.process import sequentialFrameProcessing, singleFrameProcessing
from .iMarker_sensors.sensors.config.presets import cameraMatrix_RealSense, distCoeffs_RealSense
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_offVid(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']
    isSequential = cfgMode['temporalSubtraction']

    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
    print(
        f'Framework started! [Offline Video Captured by Single Vision Setup - {setupVariant}]')

    # Check if the video file exists
    if not os.path.exists(cfgOffline['video']['path']):
        print("Video file does not exist!")
        return

    # Variables
    prevFrame = None
    frameMask = None
    singleCamera = True
    frameMaskApplied = None

    # Open the video file
    cap = cv.VideoCapture(cfgOffline['video']['path'])

    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    # Read the first frame to get the size
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    initFrame = np.zeros((height, width, 3), dtype=np.uint8)
    initFrame = resizeFrame(initFrame, cfgGui['imageHolderWidth'])
    height, width = initFrame.shape[:2]

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
    postInitImages = [(initFrame, 'FramesMain'),
                      (initFrame, 'FramesLeft'),
                      (initFrame, 'FramesRight'),
                      (initFrame, 'FramesMask'),
                      (initFrame, 'FramesMaskApplied'),
                      (initFrame, 'FramesMarker')
                      ]

    def updateAfterGui():
        for img, tag in postInitImages:
            updateImageTexture(img, tag)
    dpg.set_frame_callback(1, updateAfterGui)

    # Define textures
    with dpg.texture_registry(show=True):
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesMain")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesLeft")
        dpg.add_dynamic_texture(width, height, default_value=[
                                0.0, 0.0, 0.0, 1.0]*width*height, tag="FramesRight")
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

        # Retrieve frames
        ret, currFrame = cap.read()

        # Break out of the loop if the video is finished
        if not ret:
            break

        # Resize frames if necessary
        currFrame = resizeFrame(currFrame, cfgGui['imageHolderWidth'])

        # Rotate the frame 180 degrees (if necessary)
        if cfgOffline['video']['rotate']:
            currFrame = cv.rotate(currFrame, cv.ROTATE_180)

        # Only the first time, copy the current frame to the previous frame
        if prevFrame is None:
            prevFrame = np.copy(currFrame)

        # Update the color preview
        # updateColorPreview(
        #     window, config['algorithm']['process']['colorRange'])

        # Change brightness
        prevFrame = cv.convertScaleAbs(prevFrame, alpha=alpha, beta=beta)
        currFrame = cv.convertScaleAbs(currFrame, alpha=alpha, beta=beta)

        if (isSequential):
            # Process the frames
            prevFrame, currFrame, frameMask = sequentialFrameProcessing(
                prevFrame, currFrame, True, config)
            # Apply the mask
            frameMaskApplied = cv.bitwise_and(
                currFrame, currFrame, mask=frameMask)
        else:
            # Process the frames
            currFrame, frameMask = singleFrameProcessing(
                currFrame, True, config)
            frameMaskApplied = cv.bitwise_and(
                currFrame, currFrame, mask=frameMask)

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
            'left': prevFrame,
            'right': currFrame,
            'main': currFrame,
            'mask': frameMask,
            'maskApplied': frameMaskApplied,
            'marker': frameMarkers
        })

        # Record the frame(s)
        if dpg.get_value("RecordFlag"):
            imageList = [prevFrame, currFrame, frameMarkers] if (
                isSequential) else [currFrame, frameMarkers]
            frameSave(concatedImage, cfgMode['runner'])
            concatedImage = concatFramesHorizontal(imageList, 1800)
            dpg.set_value("RecordFlag", False)

        # You can manually stop by using stop_dearpygui()
        dpg.render_dearpygui_frame()

        # Save the previous frame
        prevFrame = np.copy(currFrame)

    print(
        f'Framework stopped! [Offline Video Captured by Single Vision Setup - {setupVariant}]')
    cv.destroyAllWindows()
    dpg.destroy_context()
