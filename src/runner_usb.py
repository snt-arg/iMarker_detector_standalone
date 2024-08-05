# import cv2 as cv
# import src.csr_sensors.sensors.sensorUSB as usb
# from src.csr_detector.process import processStereoFrames
# from src.gui.guiElements_old import getGUI, checkTerminateGUI
# from config import ports, fpsBoost, flipImage, preAligment, homographyMat, windowWidth, windowLocation


def runner_usb(config):
    print('Framework started! [USB Cameras Setup]')

#     # Create the window
#     window = getGUI(windowLocation[0], windowLocation[1])

#     capL = usb.createCameraObject(ports['lCam'])
#     capR = usb.createCameraObject(ports['rCam'])

#     if fpsBoost:
#         capL.set(cv.CAP_PROP_FPS, 30.0)
#         capR.set(cv.CAP_PROP_FPS, 30.0)

#     while True:
#         event, values = window.read(timeout=10)

#         # End program if user closes window
#         if checkTerminateGUI(event):
#             break

#         # Retrieve frames
#         # Note: if each of the cameras not working, retX will be False
#         retL, frameL = usb.grabImage(capL)
#         retR, frameR = usb.grabImage(capR)

#         # Get the values from the GUI
#         params = {'maxFeatures': values['MaxFeat'], 'goodMatchPercentage': values['MatchRate'],
#                   'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
#                   'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
#                   'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
#                   'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
#                   'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
#                   'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
#                   'preAligment': preAligment, 'homographyMat': homographyMat, 'windowWidth': windowWidth,
#                   'invertBinaryImage': values['invertBinaryImage']
#                   }

#         # Change brightness
#         frameL = cv.convertScaleAbs(
#             frameL, alpha=values['camAlpha'], beta=values['camBeta'])
#         frameR = cv.convertScaleAbs(
#             frameR, alpha=values['camAlpha'], beta=values['camBeta'])

#         # Flip the right frame
#         if (flipImage):
#             frameR = cv.flip(frameR, 1)

#         # Process frames
#         frameL, frameR, mask = processStereoFrames(
#             frameL, frameR, retL, retR, params)

#         # Add text to the image
#         # addLabel(frame, 5)

#         # Show the frames
#         frameL = cv.imencode(".png", frameL)[1].tobytes()
#         frameR = cv.imencode(".png", frameR)[1].tobytes()
#         mask = cv.imencode(".png", mask)[1].tobytes()
#         window['FramesLeft'].update(data=frameL)
#         window['FramesRight'].update(data=frameR)
#         window['FramesMask'].update(data=mask)

#     capL.release()
#     capR.release()
#     window.close()
#     print('Framework finished! [USB Cameras Setup]')
