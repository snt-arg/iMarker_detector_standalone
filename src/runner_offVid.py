import os
import cv2 as cv
import numpy as np
from .gui.utils import resizeFrame, frameSave
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame


def runner_offVid(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

    setupVariant = "Sequential Subtraction" if cfgMode['sequentialSubtraction'] else "Masking"
    print(
        f'Framework started! [Offline Video Captured by Single Vision Setup - {setupVariant}]')

    # Check if the video file exists
    if not os.path.exists(cfgOffline['video']['path']):
        print("Video file does not exist!")
        return

    # Variables
    prevFrame = None
    frameMask = None
    frameMaskApplied = None

    # Create the window
    window = getGUI(config, True)

    # Open the video file
    cap = cv.VideoCapture(cfgOffline['video']['path'])

    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Retrieve frames
            ret, currFrame = cap.read()

            # Break out of the loop if the video is finished
            if not ret:
                break

            # Change brightness
            currFrame = cv.convertScaleAbs(
                currFrame, alpha=values['camAlpha'], beta=values['camBeta'])

            # Rotate the frame 180 degrees (if necessary)
            if cfgOffline['video']['rotate']:
                currFrame = cv.rotate(currFrame, cv.ROTATE_180)

            # Only the first time, copy the current frame to the previous frame
            if prevFrame is None:
                prevFrame = np.copy(currFrame)

            # Check variable changes from the GUI
            config['marker']['structure']['leftHanded'] = values['MarkerLeftHanded']
            config['algorithm']['postprocess']['erosionKernelSize'] = values['Erosion']
            config['algorithm']['postprocess']['gaussianKernelSize'] = values['Gaussian']
            config['algorithm']['postprocess']['threshold']['size'] = values['Threshold']
            config['algorithm']['postprocess']['invertBinary'] = values['invertBinaryImage']
            # Thresholding value
            thresholdMethod = 'otsu' if values['ThreshOts'] else 'both' if values['ThreshBoth'] else 'binary'
            config['algorithm']['postprocess']['threshold']['method'] = thresholdMethod
            # Channel selection
            channel = 'r' if values['RChannel'] else 'g' if values['GChannel'] else 'b' if values['BChannel'] else 'all'
            config['algorithm']['process']['channel'] = channel

            # Resize frames if necessary
            prevFrame = resizeFrame(prevFrame, cfgGui['maxImageHolderSize'])
            currFrame = resizeFrame(currFrame, cfgGui['maxImageHolderSize'])

            if (cfgMode['sequentialSubtraction']):
                # Process the frames
                pFrame, cFrame, frameMask = processSequentialFrames(
                    prevFrame, currFrame, True, config)
                # Apply the mask
                frameMaskApplied = cv.bitwise_and(
                    cFrame, cFrame, mask=frameMask)
                # Show the setup-specific frames
                pFrameVis = cv.imencode(".png", prevFrame)[1].tobytes()
                cFrameVis = cv.imencode(".png", currFrame)[1].tobytes()
                window['FramesLeft'].update(data=pFrameVis)
                window['FramesRight'].update(data=cFrameVis)
            else:
                # Process the frames
                cFrame, frameMask = processSingleFrame(
                    currFrame, True, config)
                # Apply the mask
                frameMaskApplied = cv.bitwise_and(
                    cFrame, cFrame, mask=frameMask)
                # Show the setup-specific frames
                cFrameVis = cv.imencode(".png", currFrame)[1].tobytes()
                window['FramesMain'].update(data=cFrameVis)

            # Show the common frames
            maskVis = cv.imencode(".png", frameMask)[1].tobytes()
            maskAppliedVis = cv.imencode(".png", frameMaskApplied)[1].tobytes()
            window['FramesMask'].update(data=maskVis)
            window['FramesMaskApplied'].update(data=maskAppliedVis)

            # ArUco marker detection
            frameMarkers = arucoMarkerDetector(
                frameMask, cfgMarker['detection']['dictionary'])
            frameMarkersVis = cv.imencode(
                ".png", frameMarkers)[1].tobytes()
            window['FramesMarker'].update(data=frameMarkersVis)

            # Record the frame(s)
            if event == 'Record':
                frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
                imageList = [prevFrame, currFrame, frameMarkers] if (
                    cfgMode['sequentialSubtraction']) else [currFrame, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])

            # Save the previous frame
            prevFrame = np.copy(currFrame)

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print(
            f'Framework stopped! [Offline Video Captured by Single Vision Setup - {setupVariant}]')
