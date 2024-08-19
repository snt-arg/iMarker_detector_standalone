import cv2 as cv
import numpy as np
from .gui.utils import frameSave
from .csr_sensors.sensors import sensorRealSense
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector
from .csr_detector.process import processSequentialFrames, processSingleFrame


def runner_rs(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgRS = config['sensor']['realSense']

    setupVariant = "Sequential Subtraction" if cfgMode['sequentialSubtraction'] else "Masking"
    print(
        f'Framework started! [RealSense Single Vision Setup - {setupVariant}]')

    # Variables
    prevFrame = None
    frameMask = None
    frameMaskApplied = None

    # Create an object
    resolution = (cfgRS['resolution']['width'], cfgRS['resolution']['height'])
    rs = sensorRealSense.rsCamera(resolution, cfgRS['fps'])

    # Create a pipeline
    rs.createPipeline()

    # Start the pipeline
    rs.startPipeline()

    # Create the window
    window = getGUI(config, True)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # End program if user closes window
            frames = rs.grabFrames()

            # Get the color frame
            currFrame, camParams = rs.getColorFrame(frames)

            # Change brightness
            currFrame = cv.convertScaleAbs(
                currFrame, alpha=values['camAlpha'], beta=values['camBeta'])

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
                # Keep the original frame
                cFrameRGB = np.copy(currFrame)
                # Process the frames
                cFrame, frameMask = processSingleFrame(
                    currFrame, True, config)
                # Apply the mask
                frameMaskApplied = cv.bitwise_and(
                    cFrame, cFrame, mask=frameMask)
                # Show the setup-specific frames
                cFrameVis = cv.imencode(".png", cFrameRGB)[1].tobytes()
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
        rs.stopPipeline()
        cv.destroyAllWindows()
        print(
            f'Framework stopped! [RealSense Single Vision Setup - {setupVariant}]')
