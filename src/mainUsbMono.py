# import cv2 as cv
# import numpy as np
# import src.csr_sensors.sensors.sensorUSB as usb
# from src.gui.guiElements_old import getGUI, checkTerminateGUI
# from src.csr_detector.process import processSequentialFrames
# from config import ports, fpsBoost, windowWidth, windowLocation


# def mainUSBMono(config):
#     print('Framework started! [USB Camera Mono Setup]')

#     # Create the window
#     window = getGUI(windowLocation[0], windowLocation[1], True)

#     # Capture frames
#     cap = usb.createCameraObject(ports['lCam'])

#     # Previous frame
#     prevFrame = None

#     if fpsBoost:
#         cap.set(cv.CAP_PROP_FPS, 30.0)

#     while True:
#         event, values = window.read(timeout=10)

#         # End program if user closes window
#         if checkTerminateGUI(event):
#             break

#         # Retrieve frames
#         ret, frame = usb.grabImage(cap)

#         # Get the values from the GUI
#         params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
#                   'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
#                   'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
#                   'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
#                   'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
#                   'windowWidth': windowWidth, 'invertBinaryImage': values['invertBinaryImage'],
#                   }

#         # Check if the frame is successfully read
#         if not ret:
#             print("Failed to read a frame from the camera.")
#             break

#         # Change brightness
#         frame = cv.convertScaleAbs(
#             frame, alpha=values['camAlpha'], beta=values['camBeta'])

#         if prevFrame is None:
#             prevFrame = frame

#         # Process frames
#         prevFrame, currFrame, mask = processSequentialFrames(
#             prevFrame, frame, ret, params)

#         # Show the frames
#         prevFrame = cv.imencode(".png", prevFrame)[1].tobytes()
#         currFrame = cv.imencode(".png", currFrame)[1].tobytes()
#         mask = cv.imencode(".png", mask)[1].tobytes()
#         window['FramesLeft'].update(data=prevFrame)
#         window['FramesRight'].update(data=currFrame)
#         window['FramesMask'].update(data=mask)

#         # Save the previous frame
#         prevFrame = np.copy(frame)

#     cap.release()
#     window.close()
#     print('Framework finished! [USB Camera Mono Setup]')
