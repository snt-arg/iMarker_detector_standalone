import os
import cv2 as cv
import numpy as np
from .gui.utils import resizeFrame, frameSave
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame


def runner_offImg(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgOffline = config['sensor']['offline']

    setupVariant = "Sequential Subtraction" if cfgMode['sequentialSubtraction'] else "Masking"
    print(f'Framework started! [Offline Image Setup - {setupVariant}]')

    # Check if the images files exist
    image1Path = os.path.join(
        cfgOffline['image']['folder'], cfgOffline['image']['names'][0])
    image2Path = os.path.join(
        cfgOffline['image']['folder'], cfgOffline['image']['names'][1])
    if not os.path.exists(image1Path) or not os.path.exists(image2Path):
        print("At leaset one image does not exist!")
        return

    # Create the window
    window = getGUI(config, True)

    # Open the image files
    frame1Raw = cv.imread(image1Path)
    frame2Raw = cv.imread(image2Path)

    # Resize frames if necessary
    frame1Raw = resizeFrame(frame1Raw)
    frame2Raw = resizeFrame(frame2Raw)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Change brightness
            frame1Raw = cv.convertScaleAbs(
                frame1Raw, alpha=values['camAlpha'], beta=values['camBeta'])
            frame2Raw = cv.convertScaleAbs(
                frame2Raw, alpha=values['camAlpha'], beta=values['camBeta'])

            # Convert to HSV
            colorFrame1 = cv.cvtColor(frame1Raw, cv.COLOR_BGR2HSV)
            colorFrame2 = cv.cvtColor(frame2Raw, cv.COLOR_BGR2HSV)

            if (cfgMode['sequentialSubtraction']):
                pFrame, cFrame, mask = processSequentialFrames(
                    colorFrame1, colorFrame2, True, config)
                # Apply the mask
                frameMasked = cv.bitwise_and(pFrame, pFrame, mask=mask)
            else:
                frame, mask = processSingleFrame(colorFrame1, True, config)
                # Apply the mask
                frameMasked = cv.bitwise_and(frame, frame, mask=mask)

            # Show the frames
            if (cfgMode['sequentialSubtraction']):
                pFrame = cv.imencode(".png", pFrame)[1].tobytes()
                cFrame = cv.imencode(".png", cFrame)[1].tobytes()
                window['FramesLeft'].update(data=pFrame)
                window['FramesRight'].update(data=cFrame)
            else:
                frame = cv.imencode(".png", frame1Raw)[1].tobytes()
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

            # Record the frame(s)
            if event == 'Record':
                concatedImage = imageConcatHorizontal(
                    [frame1Raw, frame2Raw, frameMasked], 800)
                frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print(
            f'Framework stopped! [Offline Image Setup - {setupVariant}]')
