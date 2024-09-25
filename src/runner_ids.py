import os
import cv2 as cv
import numpy as np
from .csr_sensors.sensors import sensorIDS
from .gui.utils import frameSave, resizeFrame
from .csr_detector.process import processStereoFrames
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_sensors.sensors.config.idsPresets import homographyMat
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector


def runner_ids(config):
    # Get the config values
    cfgGui = config['gui']
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgIDSCam = config['sensor']['ids']

    print(f'Framework started! [Double Vision iDS Cameras Setup]')

    # Create the window
    window = getGUI(config, False)

    # Fetch the cameras
    cap1 = sensorIDS.idsCamera(0)
    cap2 = sensorIDS.idsCamera(1)

    # Get the calibration configuration
    root = f"{os.getcwd()}/src/csr_sensors/sensors/config"
    cap1.getCalibrationConfig(root, 'cam1')
    cap2.getCalibrationConfig(root, 'cam2')

    # Set the ROI
    cap1.setROI(cfgIDSCam['roi']['cap1']['x'], cfgIDSCam['roi']['cap1']
                ['y'], cfgIDSCam['roi']['cap1']['width'], cfgIDSCam['roi']['cap1']['height'])
    cap2.setROI(cfgIDSCam['roi']['cap2']['x'], cfgIDSCam['roi']['cap2']
                ['y'], cfgIDSCam['roi']['cap2']['width'], cfgIDSCam['roi']['cap2']['height'])

    # Synchronize the cameras
    cap1.syncAsMaster()
    cap2.syncAsSlave()

    # Capture the frames
    cap1.startAquisition()
    cap2.startAquisition()

    # Set the exposure time
    cap1.setExposureTime(cfgIDSCam['exposureTime'])
    cap2.setExposureTime(cfgIDSCam['exposureTime'])

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Fetch the frames
            frame1Raw = cap1.getFrame()
            frame2Raw = cap2.getFrame()

            retL = False if (not np.any(frame1Raw)) else True
            retR = False if (not np.any(frame2Raw)) else True

            # Change brightness
            frame1Raw = cv.convertScaleAbs(
                frame1Raw, alpha=values['camAlpha'], beta=values['camBeta'])
            frame2Raw = cv.convertScaleAbs(
                frame2Raw, alpha=values['camAlpha'], beta=values['camBeta'])

            # Resize frames if necessary
            frame1Raw = resizeFrame(frame1Raw, cfgGui['maxImageHolderSize'])
            frame2Raw = resizeFrame(frame2Raw, cfgGui['maxImageHolderSize'])

            # Flip the right frame
            frame2Raw = cv.flip(frame2Raw, 1)

            # Check variable changes from the GUI
            config['algorithm']['process']['subtractRL'] = values['SubtractionOrder']
            config['algorithm']['postprocess']['erosionKernelSize'] = values['Erosion']
            config['algorithm']['postprocess']['gaussianKernelSize'] = values['Gaussian']
            config['algorithm']['postprocess']['threshold']['size'] = values['Threshold']
            config['algorithm']['process']['alignment']['matchRate'] = values['MatchRate']
            config['algorithm']['process']['alignment']['maxFeatures'] = values['MaxFeat']
            config['algorithm']['postprocess']['invertBinary'] = values['invertBinaryImage']
            # Thresholding value
            thresholdMethod = 'otsu' if values['ThreshOts'] else 'both' if values['ThreshBoth'] else 'binary'
            config['algorithm']['postprocess']['threshold']['method'] = thresholdMethod
            # Channel selection
            channel = 'r' if values['RChannel'] else 'g' if values['GChannel'] else 'b' if values['BChannel'] else 'all'
            config['algorithm']['process']['channel'] = channel

            # Add the homography matrix to the config
            config['presetMat'] = homographyMat

            # Process frames
            frame1, frame2, frameMask = processStereoFrames(
                frame1Raw, frame2Raw, retL, retR, config, False)

            # Prepare a notFound image
            notFoundImage = cv.imread(
                f"{os.getcwd()}/src/notFound.png", cv.IMREAD_COLOR)

            # Convert to RGB
            frameMask = cv.cvtColor(frameMask, cv.COLOR_GRAY2BGR)

            # Show the frames
            frame1Raw = frame1Raw if retL else notFoundImage
            frame2Raw = frame2Raw if retR else notFoundImage
            frameMask = frameMask if (retR and retL) else notFoundImage
            maskVis = cv.imencode(".png", frameMask)[1].tobytes()
            frame1RawVis = cv.imencode(".png", frame1Raw)[1].tobytes()
            frame2RawVis = cv.imencode(".png", frame2Raw)[1].tobytes()
            window['FramesMask'].update(data=maskVis)
            window['FramesLeft'].update(data=frame1RawVis)
            window['FramesRight'].update(data=frame2RawVis)

            # ArUco marker detection
            frameMarkers = arucoMarkerDetector(
                frameMask, cfgMarker['detection']['dictionary'])
            frameMarkersVis = cv.imencode(
                ".png", frameMarkers)[1].tobytes()
            window['FramesMarker'].update(data=frameMarkersVis)

            # Record the frame(s)
            if event == 'Record':
                # frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
                imageList = [frame1Raw, frame2Raw, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        window.close()
        cap1.closeLibrary()
        cap2.closeLibrary()
        cv.destroyAllWindows()
        print(f'Framework finished! [Double Vision iDS Cameras Setup]')
