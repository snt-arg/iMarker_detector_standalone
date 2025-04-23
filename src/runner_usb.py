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
from .gui.utils import frameSave
import dearpygui.dearpygui as dpg
from .csr_sensors.sensors import sensorUSB as usb
from .csr_detector.process import processStereoFrames
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_sensors.sensors.calibration.utils import getCalibrationParams
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_usb(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgUsbCam = config['sensor']['usbCam']
    cfgGeneral = config['sensor']['general']

    # Get the calibration parameters
    calibrationFilePath = cfgUsbCam['calibrationPath']
    stereoMapL_x, stereoMapL_y, stereoMapR_x, stereoMapR_y = getCalibrationParams(
        calibrationFilePath)

    print(f'Framework started! [Double Vision USB Cameras Setup]')

    # Fetch the cameras
    capL = usb.createCameraObject(cfgUsbCam['ports']['lCam'])
    capR = usb.createCameraObject(cfgUsbCam['ports']['rCam'])

    if cfgGeneral['fpsBoost']:
        capL.set(cv.CAP_PROP_FPS, 30.0)
        capR.set(cv.CAP_PROP_FPS, 30.0)

    # Read the first frame to get the size
    width = int(capL.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(capL.get(cv.CAP_PROP_FRAME_HEIGHT))
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

            # Retrieve frames
            # Note: if each of the cameras not working, retX will be False
            retL, frameLRaw = usb.grabImage(capL)
            retR, frameRRaw = usb.grabImage(capR)

            # Check if both cameras are connected
            if not retL and not retR:
                print('- [Error] no camera is connected! Exiting...')
                break

            # Re-write the config values based on the GUI changes
            config['sensor']['usbCam']['maskSize'] = dpg.get_value(
                'CircMask')
            config['sensor']['usbCam']['enableMask'] = dpg.get_value(
                'CircMaskEnable')
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

            # Flip the right frame
            if (cfgUsbCam['flipImage']):
                frameRRaw = cv.flip(frameRRaw, 1)

            # Change brightness
            frameLRaw = cv.convertScaleAbs(frameLRaw, alpha=alpha, beta=beta)
            frameRRaw = cv.convertScaleAbs(frameRRaw, alpha=alpha, beta=beta)

            # Process frames
            frameL, frameR, frameMask = processStereoFrames(
                frameLRaw, frameRRaw, retL, retR, config, True)

            # Prepare a notFound image
            notFoundImage = cv.imread(
                f"{os.getcwd()}/src/notFound.png", cv.IMREAD_COLOR)

            # Convert to RGB
            frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

            # Show the frames
            frameLRaw = frameLRaw if retL else notFoundImage
            frameRRaw = frameRRaw if retR else notFoundImage
            frameMask = frameMask if (retR and retL) else notFoundImage

            # ArUco marker detection
            frameMarkers = arucoMarkerDetector(
                frameMask, None, None, cfgMarker['detection']['dictionary'],
                cfgMarker['structure']['size'])

            # Update the textures
            onImageViewTabChange({
                'left': frameLRaw,
                'right': frameRRaw,
                'mask': frameMask,
                'marker': frameMarkers
            })

            # Record the frame(s)
            if dpg.get_value("RecordFlag"):
                imageList = [frameLRaw, frameRRaw, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])
                dpg.set_value("RecordFlag", False)

            # You can manually stop by using stop_dearpygui()
            dpg.render_dearpygui_frame()

    finally:
        # Stop the pipeline and close the windows
        capL.release()
        capR.release()
        cv.destroyAllWindows()
        dpg.destroy_context()
        print(f'Framework finished! [Double Vision USB Cameras Setup]')
