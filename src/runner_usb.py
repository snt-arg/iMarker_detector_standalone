import cv2 as cv
from .gui.utils import frameSave
from .csr_sensors.sensors import sensorUSB as usb
from .csr_detector.process import processStereoFrames
from .gui.guiElements import checkTerminateGUI, getGUI
from .csr_detector.vision.concatImages import imageConcatHorizontal
from .marker_detector.arucoMarkerDetector import arucoMarkerDetector


def runner_usb(config):
    # Get the config values
    cfgMode = config['mode']
    cfgMarker = config['marker']
    cfgUsbCam = config['sensor']['usbCam']
    cfgGeneral = config['sensor']['general']

    print(f'Framework started! [Double Vision USB Cameras Setup]')

    # Create the window
    window = getGUI(config, False)

    # Fetch the cameras
    capL = usb.createCameraObject(cfgUsbCam['ports']['lCam'])
    capR = usb.createCameraObject(cfgUsbCam['ports']['rCam'])

    if cfgGeneral['fpsBoost']:
        capL.set(cv.CAP_PROP_FPS, 30.0)
        capR.set(cv.CAP_PROP_FPS, 30.0)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Retrieve frames
            # Note: if each of the cameras not working, retX will be False
            retL, frameLRaw = usb.grabImage(capL)
            retR, frameRRaw = usb.grabImage(capR)

            # Flip the right frame
            if (cfgUsbCam['flipImage']):
                frameRRaw = cv.flip(frameRRaw, 1)

            # Change brightness
            frameLRaw = cv.convertScaleAbs(
                frameLRaw, alpha=values['camAlpha'], beta=values['camBeta'])
            frameRRaw = cv.convertScaleAbs(
                frameRRaw, alpha=values['camAlpha'], beta=values['camBeta'])

            # Check variable changes from the GUI
            config['sensor']['usbCam']['maskSize'] = values['CircMask']
            config['sensor']['usbCam']['enableMask'] = values['CircMaskEnable']
            config['marker']['structure']['leftHanded'] = values['MarkerLeftHanded']
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

            # Process frames
            frameL, frameR, frameMask = processStereoFrames(
                frameLRaw, frameRRaw, retL, retR, config, True)

            # Show the frames
            frameLRaw = frameLRaw if retL else frameL
            frameRRaw = frameRRaw if retR else frameR
            frameMask = frameMask if (
                retR and retL) else frameR if retL else frameL
            maskVis = cv.imencode(".png", frameMask)[1].tobytes()
            frameLRawVis = cv.imencode(".png", frameLRaw)[1].tobytes()
            frameRRawVis = cv.imencode(".png", frameRRaw)[1].tobytes()
            window['FramesMask'].update(data=maskVis)
            window['FramesLeft'].update(data=frameLRawVis)
            window['FramesRight'].update(data=frameRRawVis)

            # ArUco marker detection
            frameMarkers = arucoMarkerDetector(
                frameMask, cfgMarker['detection']['dictionary'])
            frameMarkersVis = cv.imencode(
                ".png", frameMarkers)[1].tobytes()
            window['FramesMarker'].update(data=frameMarkersVis)

            # Record the frame(s)
            if event == 'Record':
                frameMarkers = cv.cvtColor(frameMarkers, cv.COLOR_GRAY2BGR)
                imageList = [frameLRaw, frameRRaw, frameMarkers]
                concatedImage = imageConcatHorizontal(imageList, 1800)
                frameSave(concatedImage, cfgMode['runner'])

    finally:
        # Stop the pipeline and close the windows
        capL.release()
        capR.release()
        cv.destroyAllWindows()
        print(f'Framework finished! [Double Vision USB Cameras Setup]')
