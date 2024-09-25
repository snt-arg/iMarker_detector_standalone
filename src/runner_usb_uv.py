import os
import cv2 as cv
from .gui.utils import frameSave
from .csr_sensors.sensors import sensorUSB as usb
from .csr_detector.process import processSingleFrame
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector


def runner_usbUV(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgUVCam = config['sensor']['usbCamUV']
    cfgGeneral = config['sensor']['general']

    print(f'Framework started! [Single-Vision UV Camera Setup]')

    # Create the window
    window = getGUI(config, True)

    # Fetch the cameras
    cap = usb.createCameraObject(cfgUVCam['port'])

    if cfgGeneral['fpsBoost']:
        cap.set(cv.CAP_PROP_FPS, 30.0)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Retrieve frames
            # Note: if each of the cameras not working, retX will be False
            ret, frameRaw = usb.grabImage(cap)

            # Check if both cameras are connected
            if not ret:
                print('- [Error] no UV camera is connected! Exiting...')
                break

            # Change brightness
            frameRaw = cv.convertScaleAbs(
                frameRaw, alpha=values['camAlpha'], beta=values['camBeta'])

            # Check variable changes from the GUI
            config['algorithm']['postprocess']['erosionKernelSize'] = values['Erosion']
            config['algorithm']['postprocess']['gaussianKernelSize'] = values['Gaussian']
            config['algorithm']['postprocess']['threshold']['size'] = values['Threshold']
            config['algorithm']['postprocess']['invertBinary'] = values['invertBinaryImage']
            # Thresholding value
            thresholdMethod = 'otsu' if values['ThreshOts'] else 'both' if values['ThreshBoth'] else 'binary'
            config['algorithm']['postprocess']['threshold']['method'] = thresholdMethod

            # Prepare a notFound image
            notFoundImage = cv.imread(
                f"{os.getcwd()}/src/notFound.png", cv.IMREAD_COLOR)

            # Process frames
            cFrame, frameMask = processSingleFrame(
                frameRaw, ret, config)

            # Apply the mask
            frameMaskApplied = cv.bitwise_and(
                cFrame, cFrame, mask=frameMask)

            # Show the frames
            frameRaw = frameRaw if ret else notFoundImage
            frameMask = frameMask if ret else notFoundImage
            maskVis = cv.imencode(".png", frameMask)[1].tobytes()
            frameRawVis = cv.imencode(".png", frameRaw)[1].tobytes()
            maskAppliedVis = cv.imencode(".png", frameMaskApplied)[1].tobytes()
            window['FramesMask'].update(data=maskVis)
            window['FramesMain'].update(data=frameRawVis)
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
                imageList = [frameRaw, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        cap.release()
        cv.destroyAllWindows()
        print(f'Framework finished! [Single-Vision UV Camera Setup]')
