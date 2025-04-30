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
from .marker_detector.arucoDetector import arucoDetector
from .iMarker_algorithms.process import singleFrameProcessing
from .iMarker_algorithms.vision.concatImages import concatFramesHorizontal
from .iMarker_sensors.sensors.config.presets import cameraMatrix_RealSense, distCoeffs_RealSense
from .gui.guiContent import guiElements, loadImageAsTexture, onImageViewTabChange, updateImageTexture, updateWindowSize


def runner_sv_off_img_uv(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

    print(
        f'Framework started! [Offline Images Captured by Single-Vision UV/IR Setup]')

    # Check if the images files exist
    imagePath = cfgOffline['imageUV']['path']
    if not os.path.exists(imagePath):
        print("Image does not exist! Exiting ...")
        return

    # Variables
    frameMask = None

    # Open the image files
    frameRawFetched = cv.imread(imagePath)

    # Resize frames if necessary
    frameRawFetched = resizeFrame(
        frameRawFetched, cfgGui['imageHolderWidth'])

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
    postInitImages = [(frameRawFetched, 'FramesMain'),
                      (frameRawFetched, 'FramesMask'),
                      (frameRawFetched, 'FramesMaskApplied'),
                      (frameRawFetched, 'FramesMarker')
                      ]

    def updateAfterGui():
        for img, tag in postInitImages:
            updateImageTexture(img, tag)
    dpg.set_frame_callback(1, updateAfterGui)

    # Define textures
    height, width = frameRawFetched.shape[:2]
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

    # Loop
    while dpg.is_dearpygui_running():
        # Get GUI values
        alpha = dpg.get_value('camAlpha')
        beta = dpg.get_value('camBeta')

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

        frameRaw = frameRawFetched.copy()

        # Change brightness
        frameRaw = cv.convertScaleAbs(frameRaw, alpha=alpha, beta=beta)

        # Keep the original frame
        cFrameGrayscale = np.copy(frameRaw)
        # Process the frames
        cFrame, frameMask = singleFrameProcessing(
            frameRaw, True, config)
        frameMaskApplied = cv.bitwise_and(
            cFrame, cFrame, mask=frameMask)

        # Camera parameters
        distCoeffs = distCoeffs_RealSense
        cameraMatrix = cameraMatrix_RealSense

        # ArUco marker detection
        frameMarkers = arucoDetector(
            frameMask, cameraMatrix, distCoeffs, cfgMarker['detection']['dictionary'],
            cfgMarker['structure']['size'])

        # Update the textures
        onImageViewTabChange({
            'main': cFrameGrayscale,
            'mask': frameMask,
            'maskApplied': frameMaskApplied,
            'marker': frameMarkers
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

    # Stop the pipeline and close the windows
    print(
        f'Framework stopped! [Offline Images Captured by Single-Vision UV/IR Setup]')
    cv.destroyAllWindows()
    dpg.destroy_context()
