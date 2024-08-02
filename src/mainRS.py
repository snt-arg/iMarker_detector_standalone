# import cv2 as cv
# import numpy as np
# from .csr_sensors.sensors import sensorRealSense
# # from src.gui.guiElements import getGUI, checkTerminateGUI
# from config import arucoDict, arucoParams, isSequentialSubtraction
# # from src.marker_detector.arucoMarkerDetector import arucoMarkerDetector
# # from src.csr_detector.process import processSequentialFrames, processSingleFrame
# # from config import realSenseResolution, realSenseFps, windowWidth, windowLocation


def mainRealSense(config):
    print('Framework started! [RealSense Setup]')
    # monoSetupVariant = "Sequential Subtraction" if [
    #     isSequentialSubtraction] else "Masking"
    # print(f'Framework started! [RealSense Mono Setup - {monoSetupVariant}]')

#     # Create an object
#     # rs = sensorRealSense.rsCamera(realSenseResolution, realSenseFps)

#     # Create a pipeline
#     # rs.createPipeline()

#     # Start the pipeline
#     # rs.startPipeline()

#     # Create the window
#     # window = getGUI(windowLocation[0], windowLocation[1], True)

#     # Previous frame
#     # prevFrame = None

#     # try:
#     #     while True:
#     #         event, values = window.read(timeout=10)

#     #         # End program if user closes window
#     #         if checkTerminateGUI(event):
#     #             break

#     #         # Wait for the next frames from the camera
#     #         frames = rs.grabFrames()

#     #         # Get the color frame
#     #         colorFrameRaw, colorCamIntrinsics = rs.getColorFrame(frames)

#     #         # Get the values from the GUI
#     #         params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
#     #                   'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
#     #                   'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
#     #                   'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
#     #                   'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
#     #                   'windowWidth': windowWidth, 'invertBinaryImage': values['invertBinaryImage'],
#     #                   }

#     #         # Change brightness
#     #         colorFrameRaw = cv.convertScaleAbs(
#     #             colorFrameRaw, alpha=values['camAlpha'], beta=values['camBeta'])

#     #         # Convert to HSV
#     #         if (isSequentialSubtraction):
#     #             colorFrame = np.copy(colorFrameRaw)
#     #         else:
#     #             colorFrame = cv.cvtColor(colorFrameRaw, cv.COLOR_BGR2HSV)

#     #         if prevFrame is None:
#     #             prevFrame = np.copy(colorFrame)

#     #         if (isSequentialSubtraction):
#     #             pFrame, cFrame, mask = processSequentialFrames(
#     #                 prevFrame, colorFrame, True, params)
#     #             # Apply the mask
#     #             frameMasked = cv.bitwise_and(pFrame, pFrame, mask=mask)
#     #         else:
#     #             frame, mask = processSingleFrame(colorFrame, True, params)
#     #             # Apply the mask
#     #             frameMasked = cv.bitwise_and(frame, frame, mask=mask)

#     #         # Show the frames
#     #         if (isSequentialSubtraction):
#     #             pFrame = cv.imencode(".png", pFrame)[1].tobytes()
#     #             cFrame = cv.imencode(".png", cFrame)[1].tobytes()
#     #             window['FramesLeft'].update(data=pFrame)
#     #             window['FramesRight'].update(data=cFrame)
#     #         else:
#     #             frame = cv.imencode(".png", colorFrameRaw)[1].tobytes()
#     #             window['FramesMain'].update(data=frame)
#     #         newMask = cv.imencode(".png", mask)[1].tobytes()
#     #         window['FramesMask'].update(data=newMask)
#     #         newFrameMasked = cv.imencode(".png", frameMasked)[1].tobytes()
#     #         window['FramesMaskApplied'].update(data=newFrameMasked)

#     #         # ArUco marker detection
#     #         detectedMarkers = arucoMarkerDetector(
#     #             mask, arucoDict, arucoParams)
#     #         detectedMarkers = cv.imencode(".png", detectedMarkers)[1].tobytes()
#     #         window['FramesMarker'].update(data=detectedMarkers)

#     #         # Save the previous frame
#     #         prevFrame = np.copy(colorFrame)

#     # finally:
#     #     # Stop the pipeline and close the windows
#     #     rs.stopPipeline()
#     #     cv.destroyAllWindows()
#     #     print(
#     #         f'Framework stopped! [RealSense Mono Setup - {monoSetupVariant}]')
