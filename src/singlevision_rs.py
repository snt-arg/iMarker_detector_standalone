"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

import cv2 as cv
import numpy as np
import dearpygui.dearpygui as dpg
from .iMarker_sensors.sensors import rs_interface
from .marker_detector.arucoDetector import arucoDetector
from .gui.utils import frameSave, resizeFrame, rgbToHsvTuple
from .iMarker_algorithms.vision.concatImages import concatFramesHorizontal
from .iMarker_algorithms.process import sequentialFrameProcessing, singleFrameProcessing
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_sv_rs(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgRS = config['sensor']['realSense']
    isSequential = cfgMode['temporalSubtraction']

    setupVariant = "Temporal Subtraction" if isSequential else "Masking"
    print(
        f'Framework started! [Single-Vision RealSense Setup - {setupVariant}]')

    # Variables
    prevFrame = None
    frameMask = None
    frameMaskApplied = None

    # Create an object
    width = cfgRS['resolution']['width']
    height = cfgRS['resolution']['height']
    rs = rs_interface.rsCamera((width, height), cfgRS['fps'])

    # Create a pipeline
    rs.createPipeline()

    # Start the pipeline
    isPipelineStarted = rs.startPipeline()

    # Read the first frame to get the size
    initFrame = np.zeros((height, width, 3), dtype=np.uint8)

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
    postInitImages = [(initFrame, 'FramesMask'),
                      (initFrame, 'FramesMaskApplied'),
                      (initFrame, 'FramesMarker'),
                      (initFrame, 'FramesLeft'),
                      (initFrame, 'FramesRight'),
                      (initFrame, 'FramesMain')]

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
    guiElements(config, True)

    dpg.show_viewport()

    try:
        while dpg.is_dearpygui_running():
            # Get GUI values
            alpha = dpg.get_value('camAlpha')
            beta = dpg.get_value('camBeta')

            # Get color range values
            greenRangeLow = rgbToHsvTuple(dpg.get_value('GreenRangeLow'))
            greenRangeHigh = rgbToHsvTuple(dpg.get_value('GreenRangeHigh'))

            # Check if the frames are valid
            if not isPipelineStarted:
                break

            # End program if user closes window
            frames = rs.grabFrames()

            # Check if the frames are valid
            if frames is None:
                break

            # Get the color frame
            currFrame, cameraMatrix, distCoeffs = rs.getColorFrame(frames)

            # Resize frames if necessary
            currFrame = resizeFrame(currFrame, 1000)

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
            config['algorithm']['process']['colorRange']['hsv_green']['lower'] = greenRangeLow
            config['algorithm']['process']['colorRange']['hsv_green']['upper'] = greenRangeHigh
            # Alignment parameters
            config['algorithm']['process']['alignment']['matchRate'] = dpg.get_value(
                'MatchRate')
            config['algorithm']['process']['alignment']['maxFeatures'] = dpg.get_value(
                'MaxFeat')
            # Thresholding value
            config['algorithm']['postprocess']['threshold']['method'] = dpg.get_value(
                'ThreshMethod').lower()
            # Channel selection
            colorChannelValue = dpg.get_value('ColorChannel')
            channel = 'r' if colorChannelValue == 'Red' else 'g' if dpg.get_value(
                'ColorChannel') == 'Green' else 'b' if colorChannelValue == 'Blue' else 'All'
            config['algorithm']['process']['channel'] = channel

            # Change brightness
            currFrame = cv.convertScaleAbs(currFrame, alpha=alpha, beta=beta)

            # Only the first time, copy the current frame to the previous frame
            if prevFrame is None:
                prevFrame = np.copy(currFrame)

            # Update the color preview
            # updateColorPreview(
            #     window, config['algorithm']['process']['colorRange'])

            if (isSequential):
                # Process the frames
                pFrame, cFrame, frameMask = sequentialFrameProcessing(
                    prevFrame, currFrame, True, config)
                # Apply the mask
                frameMaskApplied = cv.bitwise_and(
                    cFrame, cFrame, mask=frameMask)
            else:
                # Keep the original frame
                # cFrameRGB = np.copy(currFrame)
                # Process the frames
                cFrame, frameMask = singleFrameProcessing(
                    currFrame, True, config)
                # Apply the mask
                frameMaskApplied = cv.bitwise_and(
                    cFrame, cFrame, mask=frameMask)

            # Convert to RGB
            frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

            # ArUco marker detection
            frameMarkers = arucoDetector(
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
                concatedImage = concatFramesHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])
                dpg.set_value("RecordFlag", False)

            # You can manually stop by using stop_dearpygui()
            dpg.render_dearpygui_frame()

            # Save the previous frame
            prevFrame = np.copy(currFrame)

    finally:
        # Stop the pipeline and close the windows
        if isPipelineStarted:
            rs.stopPipeline()
        cv.destroyAllWindows()
        dpg.destroy_context()
        print(
            f'Framework stopped! [Single-Vision RealSense Setup - {setupVariant}]')
