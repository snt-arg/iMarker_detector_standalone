import os
import cv2 as cv
import numpy as np
from .gui.utils import resizeFrame, frameSave
from .csr_detector.process import processSingleFrame
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector


def runner_offImgUV(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

    print(f'Framework started! [Offline Images Captured by UV Vision Setup]')

    # Check if the images files exist
    imagePath = cfgOffline['imageUV']['path']
    if not os.path.exists(imagePath):
        print("Image does not exist! Exiting ...")
        return

    # Variables
    frameMask = None

    # Create the window
    window = getGUI(config, True)

    # Open the image files
    frameRawFetched = cv.imread(imagePath)

    # Resize frames if necessary
    frameRawFetched = resizeFrame(
        frameRawFetched, cfgGui['maxImageHolderSize'])

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            frameRaw = frameRawFetched.copy()

            # Change brightness
            frameRaw = cv.convertScaleAbs(
                frameRaw, alpha=values['camAlpha'], beta=values['camBeta'])

            # Check variable changes from the GUI
            config['algorithm']['postprocess']['erosionKernelSize'] = values['Erosion']
            config['algorithm']['postprocess']['gaussianKernelSize'] = values['Gaussian']
            config['algorithm']['postprocess']['threshold']['size'] = values['Threshold']
            config['algorithm']['postprocess']['invertBinary'] = values['invertBinaryImage']
            # Thresholding value
            thresholdMethod = 'otsu' if values['ThreshOts'] else 'adaptive' if values['ThreshAdapt'] else 'binary'
            config['algorithm']['postprocess']['threshold']['method'] = thresholdMethod

            # Keep the original frame
            cFrameGrayscale = np.copy(frameRaw)
            # Process the frames
            cFrame, frameMask = processSingleFrame(
                frameRaw, True, config)
            frameMaskApplied = cv.bitwise_and(
                cFrame, cFrame, mask=frameMask)
            # Show the setup-specific frames
            cFrameVis = cv.imencode(".png", cFrameGrayscale)[1].tobytes()
            window['FramesMain'].update(data=cFrameVis)

            # Show the common frames
            maskVis = cv.imencode(".png", frameMask)[1].tobytes()
            maskAppliedVis = cv.imencode(".png", frameMaskApplied)[1].tobytes()
            window['FramesMask'].update(data=maskVis)
            window['FramesMaskApplied'].update(data=maskAppliedVis)

            # ArUco marker detection
            frameMarkers = arucoMarkerDetector(
                frameMask, None, None, cfgMarker['detection']['dictionary'],
                cfgMarker['structure']['size'])
            frameMarkersVis = cv.imencode(
                ".png", frameMarkers)[1].tobytes()
            window['FramesMarker'].update(data=frameMarkersVis)

            # Record the frame(s)
            if event == 'Record':
                frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
                imageList = [frameRaw, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print(
            f'Framework stopped! [Offline Images Captured by UV Vision Setup]')
