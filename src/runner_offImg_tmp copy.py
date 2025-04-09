import os
import cv2 as cv
import numpy as np
from .gui.utils import resizeFrame, frameSave
from .utils import startProfiler, stopProfiler
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame
from .gui.guiContent import guiCloseCallback, guiIsRunning, getGUI, updateColorPreview, renderFrame, getGUIValue
from .csr_sensors.sensors.config.cameraPresets import cameraMatrix_RealSense, distCoeffs_RealSense


def runner_offImg(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

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

    # Create the window
    getGUI(config, True, imageSize=frame1RawFetched.shape, postInitImages=[
        (frame1RawFetched, 'FramesMain')
    ])

    # Start the profiler
    # profiler = startProfiler()

    try:
        while guiIsRunning():
            print("Running ...")
            frame1Raw = frame1RawFetched.copy()
            frame2Raw = frame2RawFetched.copy()

    #         # Change brightness
    #         alpha = getGUIValue('camAlpha')
    #         beta = getGUIValue('camBeta')
    #         print("Alpha: ", alpha, beta)
    #         frame1Raw = cv.convertScaleAbs(frame1Raw, alpha, beta)
    #         frame2Raw = cv.convertScaleAbs(frame2Raw, alpha, beta)

    #         # Check variable changes from the GUI
    #         config['algorithm']['process']['subtractRL'] = values['SubtractionOrder']
    #         config['algorithm']['postprocess']['erosionKernelSize'] = values['Erosion']
    #         config['algorithm']['postprocess']['gaussianKernelSize'] = values['Gaussian']
    #         config['algorithm']['postprocess']['threshold']['size'] = values['Threshold']
    #         config['algorithm']['postprocess']['invertBinary'] = values['invertBinaryImage']
    #         config['algorithm']['process']['colorRange']['hsv_green']['lower'][0] = int(
    #             values['GreenRangeHueLow'])
    #         config['algorithm']['process']['colorRange']['hsv_green']['lower'][1] = int(
    #             values['GreenRangeSatLow'])
    #         config['algorithm']['process']['colorRange']['hsv_green']['upper'][0] = int(
    #             values['GreenRangeHueHigh'])
    #         config['algorithm']['process']['colorRange']['hsv_green']['upper'][1] = int(
    #             values['GreenRangeSatHigh'])
    #         # Thresholding value
    #         thresholdMethod = 'otsu' if values['ThreshOts'] else 'adaptive' if values['ThreshAdapt'] else 'binary'
    #         config['algorithm']['postprocess']['threshold']['method'] = thresholdMethod
    #         # Channel selection
    #         channel = 'r' if values['RChannel'] else 'g' if values['GChannel'] else 'b' if values['BChannel'] else 'all'
    #         config['algorithm']['process']['channel'] = channel

    #         # Update the color preview
    #         updateColorPreview(
    #             window, config['algorithm']['process']['colorRange'])

    #         if (cfgMode['sequentialSubtraction']):
    #             # Process the frames
    #             pFrame, cFrame, frameMask = processSequentialFrames(
    #                 frame1Raw, frame2Raw, True, config)
    #             # Apply the mask
    #             frameMaskApplied = cv.bitwise_and(
    #                 cFrame, cFrame, mask=frameMask)
    #             # Show the setup-specific frames
    #             pFrameVis = cv.imencode(".png", frame1Raw)[1].tobytes()
    #             cFrameVis = cv.imencode(".png", frame2Raw)[1].tobytes()
    #             window['FramesLeft'].update(data=pFrameVis)
    #             window['FramesRight'].update(data=cFrameVis)
    #         else:
    #             # Keep the original frame
    #             cFrameRGB = np.copy(frame2Raw)
    #             # Process the frames
    #             cFrame, frameMask = processSingleFrame(
    #                 frame2Raw, True, config)
    #             frameMaskApplied = cv.bitwise_and(
    #                 cFrame, cFrame, mask=frameMask)
    #             # Show the setup-specific frames
    #             cFrameVis = cv.imencode(".png", cFrameRGB)[1].tobytes()
    #             window['FramesMain'].update(data=cFrameVis)

    #         # Show the common frames
    #         maskVis = cv.imencode(".png", frameMask)[1].tobytes()
    #         maskAppliedVis = cv.imencode(".png", frameMaskApplied)[1].tobytes()
    #         window['FramesMask'].update(data=maskVis)
    #         window['FramesMaskApplied'].update(data=maskAppliedVis)

    #         # Convert to RGB
    #         frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

    #         # Camera parameters
    #         distCoeffs = distCoeffs_RealSense
    #         cameraMatrix = cameraMatrix_RealSense

    #         # ArUco marker detection
    #         frameMarkers = arucoMarkerDetector(
    #             frameMask, cameraMatrix, distCoeffs, cfgMarker['detection']['dictionary'],
    #             cfgMarker['structure']['size'])
    #         frameMarkersVis = cv.imencode(
    #             ".png", frameMarkers)[1].tobytes()
    #         window['FramesMarker'].update(data=frameMarkersVis)

    #         # Record the frame(s)
    #         if event == 'Record':
    #             # frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
    #             imageList = [frame1Raw, frame2Raw, frameMarkers] if (
    #                 cfgMode['sequentialSubtraction']) else [frame2Raw, frameMarkers]
    #             concatedImage = imageConcatHorizontal(imageList, 1800)
    #             frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        guiCloseCallback()
        print(
            f'Framework stopped! [Offline Images Captured by Single Vision Setup - {setupVariant}]')
    # stopProfiler(profiler)
