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
from .iMarker_sensors.sensors import ids_interface
from .marker_detector.arucoDetector import arucoDetector
from .gui.utils import frameSave, resizeFrame, rgbToHsvTuple
from .iMarker_algorithms.process import stereoFrameProcessing
from .iMarker_algorithms.vision.concatImages import concatFramesHorizontal
from .iMarker_sensors.sensors.config.presets import homographyMatrixPreset_iDS
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_ids(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgIDSCam = config['sensor']['ids']

    print(f'Framework started! [Double Vision iDS Cameras Setup]')

    # Fetch the cameras
    cap1 = ids_interface.idsCamera(0)
    cap2 = ids_interface.idsCamera(1)

    # Get the calibration configuration
    root = f"{os.getcwd()}/src/iMarker_sensors/sensors/config"
    cap1.getCalibrationConfig(root, 'cam1')
    cap2.getCalibrationConfig(root, 'cam2')

    # Set the ROI
    cap1.setROI(cfgIDSCam['roi']['cap1']['x'], cfgIDSCam['roi']['cap1']
                ['y'], cfgIDSCam['roi']['cap1']['width'], cfgIDSCam['roi']['cap1']['height'])
    cap2.setROI(cfgIDSCam['roi']['cap2']['x'], cfgIDSCam['roi']['cap2']
                ['y'], cfgIDSCam['roi']['cap2']['width'], cfgIDSCam['roi']['cap2']['height'])

    # Synchronize the cameras
    cap1.syncAsMaster()
    cap2.syncAsSlave()

    # Capture the frames
    cap1.startAquisition()
    cap2.startAquisition()

    # Set the exposure time
    cap1.setExposureTime(cfgIDSCam['exposureTime'])
    cap2.setExposureTime(cfgIDSCam['exposureTime'])

    # Read the first frame to get the size
    initFrame = cap1.getFrame()
    retL = False if (not np.any(initFrame)) else True
    if not retL:
        print("- Error: Could not open camera 1.")
        exit()
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
    postInitImages = [(initFrame, 'FramesLeft'),
                      (initFrame, 'FramesRight'),
                      (initFrame, 'FramesMask'),
                      (initFrame, 'FramesMaskApplied'),
                      (initFrame, 'FramesMarker')]

    def updateAfterGui():
        for img, tag in postInitImages:
            updateImageTexture(img, tag)
    dpg.set_frame_callback(1, updateAfterGui)

    # Define textures
    with dpg.texture_registry(show=True):
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
    guiElements(config)

    dpg.show_viewport()

    try:
        while dpg.is_dearpygui_running():
            # Get GUI values
            alpha = dpg.get_value('camAlpha')
            beta = dpg.get_value('camBeta')

            # Get color range values
            greenRangeLow = rgbToHsvTuple(dpg.get_value('GreenRangeLow'))
            greenRangeHigh = rgbToHsvTuple(dpg.get_value('GreenRangeHigh'))

            # Fetch the frames
            frame1Raw = cap1.getFrame()
            frame2Raw = cap2.getFrame()

            retL = False if (not np.any(frame1Raw)) else True
            retR = False if (not np.any(frame2Raw)) else True

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
            frame1Raw = cv.convertScaleAbs(frame1Raw, alpha=alpha, beta=beta)
            frame2Raw = cv.convertScaleAbs(frame2Raw, alpha=alpha, beta=beta)

            # Resize frames if necessary
            frame1Raw = resizeFrame(frame1Raw, cfgGui['imageHolderWidth'])
            frame2Raw = resizeFrame(frame2Raw, cfgGui['imageHolderWidth'])

            # Flip the right frame
            frame2Raw = cv.flip(frame2Raw, 1)

            # Add the homography matrix to the config
            config['presetMat'] = homographyMatrixPreset_iDS

            # Process frames
            frame1, frame2, frameMask = stereoFrameProcessing(
                frame1Raw, frame2Raw, retL, retR, config, False)

            # Prepare a notFound image
            notFoundImage = cv.imread(
                f"{os.getcwd()}/src/notFound.png", cv.IMREAD_COLOR)

            # Convert to RGB
            frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

            # Show the frames
            frame1Raw = frame1Raw if retL else notFoundImage
            frame2Raw = frame2Raw if retR else notFoundImage
            frameMask = frameMask if (retR and retL) else notFoundImage

            # ArUco marker detection
            frameMarkers = arucoDetector(
                frameMask, None, None, cfgMarker['detection']['dictionary'],
                cfgMarker['structure']['size'])

            # Update the textures
            onImageViewTabChange({
                'left': frame1Raw,
                'right': frame2Raw,
                'mask': frameMask,
                'marker': frameMarkers
            })

            # Record the frame(s)
            if dpg.get_value("RecordFlag"):
                imageList = [frame1Raw, frame2Raw, frameMarkers]
                concatedImage = concatFramesHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])
                dpg.set_value("RecordFlag", False)

            # You can manually stop by using stop_dearpygui()
            dpg.render_dearpygui_frame()

    finally:
        # Stop the pipeline and close the windows
        cap1.closeLibrary()
        cap2.closeLibrary()
        cv.destroyAllWindows()
        dpg.destroy_context()
        print(f'Framework finished! [Double Vision iDS Cameras Setup]')
