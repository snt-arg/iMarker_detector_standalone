import os
import cv2 as cv
import numpy as np
from .gui.guiElements import checkTerminateGUI, getGUI
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame


def mainOfflineVideo(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

    setupVariant = "Sequential Subtraction" if cfgMode['sequentialSubtraction'] else "Masking"
    print(f'Framework started! [Offline Video Setup - {setupVariant}]')

    # Check if the video file exists
    if not os.path.exists(cfgOffline['video']['path']):
        print("Video file does not exist!")
        return

    # Create the window
    window = getGUI(config, True)

    # Open the video file
    cap = cv.VideoCapture(cfgOffline['video']['path'])

    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    # Previous frame
    prevFrame = None

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

            if prevFrame is None:
                prevFrame = np.copy(currFrame)

            # Convert to HSV
            prevFrameHSV = cv.cvtColor(prevFrame, cv.COLOR_BGR2HSV)
            currFrameHSV = cv.cvtColor(currFrame, cv.COLOR_BGR2HSV)

            if (cfgMode['sequentialSubtraction']):
                pFrame, cFrame, mask = processSequentialFrames(
                    prevFrame, currFrame, True, config)
                # Apply the mask
                frameMasked = cv.bitwise_and(pFrame, pFrame, mask=mask)
            else:
                frame, mask = processSingleFrame(currFrameHSV, True, config)
                # Apply the mask
                frameMasked = cv.bitwise_and(frame, frame, mask=mask)

            # Resize the frame while keeping the aspect ratio to fit the height of the window
            ratio = cfgGui['windowWidth'] / frame.shape[1] / 2
            dim = (cfgGui['windowWidth'], int(frame.shape[0] * ratio))
            frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

            # Show the frames
            if (cfgMode['sequentialSubtraction']):
                pFrame = cv.imencode(".png", pFrame)[1].tobytes()
                cFrame = cv.imencode(".png", cFrame)[1].tobytes()
                window['FramesLeft'].update(data=pFrame)
                window['FramesRight'].update(data=cFrame)
            else:
                frame = cv.imencode(".png", currFrame)[1].tobytes()
                window['FramesMain'].update(data=frame)
            newMask = cv.imencode(".png", mask)[1].tobytes()
            window['FramesMask'].update(data=newMask)
            newFrameMasked = cv.imencode(".png", frameMasked)[1].tobytes()
            window['FramesMaskApplied'].update(data=newFrameMasked)

            # ArUco marker detection
            detectedMarkers = arucoMarkerDetector(
                mask, cfgMarker['detection']['dictionary'])
            detectedMarkers = cv.imencode(".png", detectedMarkers)[1].tobytes()
            window['FramesMarker'].update(data=detectedMarkers)

            # Save the previous frame
            prevFrame = np.copy(currFrame)

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print('Framework stopped! [Offline Video Seq. Setup]')
