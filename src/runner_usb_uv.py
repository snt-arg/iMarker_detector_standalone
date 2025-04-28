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
from .marker_detector.arucoDetector import arucoDetector
from .iMarker_sensors.sensors import usb_interface as usb
from .iMarker_algorithms.process import singleFrameProcessing
from .iMarker_algorithms.vision.concatImages import concatFramesHorizontal
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_usbUV(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgUVCam = config['sensor']['usbCamUV']
    cfgGeneral = config['sensor']['general']

    print(f'Framework started! [Single-Vision UV Camera Setup]')

    # Fetch the cameras
    try:
        cap = usb.createCameraObject(cfgUVCam['port'])
    except Exception as e:
        print(f'- [Error] Error while fetching camera output: {e}')
        return

    if cfgGeneral['fpsBoost']:
        cap.set(cv.CAP_PROP_FPS, 30.0)

    # Read the first frame to get the size
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
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

            # Retrieve frames
            ret, frameRaw = usb.grabImage(cap)

            # Check if both cameras are connected
            if not ret:
                print('- [Error] no UV camera is connected! Exiting...')
                break

            # Re-write the config values based on the GUI changes
            config['algorithm']['postprocess']['erosionKernel'] = dpg.get_value(
                'Erosion')
            config['algorithm']['postprocess']['gaussianKernel'] = dpg.get_value(
                'Gaussian') if dpg.get_value('Gaussian') % 2 == 1 else dpg.get_value('Gaussian') + 1
            config['algorithm']['postprocess']['threshold']['size'] = dpg.get_value(
                'Threshold')
            config['algorithm']['postprocess']['invertBinary'] = dpg.get_value(
                'invertBinaryImage')
            # Thresholding value
            config['algorithm']['postprocess']['threshold']['method'] = dpg.get_value(
                'ThreshMethod').lower()

            # Change brightness
            frameRaw = cv.convertScaleAbs(frameRaw, alpha=alpha, beta=beta)

            # Prepare a notFound image
            notFoundImage = cv.imread(
                f"{os.getcwd()}/src/notFound.png", cv.IMREAD_COLOR)

            # Process frames
            cFrame, frameMask = singleFrameProcessing(
                frameRaw, ret, config)

            # Apply the mask
            frameMaskApplied = cv.bitwise_and(
                cFrame, cFrame, mask=frameMask)

            # Show the frames
            frameRaw = frameRaw if ret else notFoundImage
            frameMask = frameMask if ret else notFoundImage

            # ArUco marker detection
            frameMarkers = arucoDetector(
                frameMask, None, None, cfgMarker['detection']['dictionary'],
                cfgMarker['structure']['size'])

            # Update the textures
            onImageViewTabChange({
                'main': cFrame,
                'mask': frameMask,
                'marker': frameMarkers,
                'maskApplied': frameMaskApplied,
            })

            # Record the frame(s)
            if dpg.get_value("RecordFlag"):
                frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
                imageList = [frameRaw, frameMarkers]
                concatedImage = concatFramesHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])
                dpg.set_value("RecordFlag", False)

            # You can manually stop by using stop_dearpygui()
            dpg.render_dearpygui_frame()

    finally:
        # Stop the pipeline and close the windows
        cap.release()
        cv.destroyAllWindows()
        dpg.destroy_context()
        print(f'Framework finished! [Single-Vision UV Camera Setup]')
