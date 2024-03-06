import cv2 as cv
import numpy as np
from src.csr_sensors.sensors import sensorRealSense
from src.gui.guiElements import getGUI, checkTerminateGUI
from src.csr_detector.process import processSequentialFrames, processSingleFrame
from config import realSenseResolution, realSenseFps, windowWidth, windowLocation, isSequentialSubtraction


def main():
    monoSetupVariant = "Sequential Subtraction" if isSequentialSubtraction else "Thresholding"
    print(f'Framework started! [RealSense Mono Setup - {monoSetupVariant}]')

    # Create an object
    rs = sensorRealSense.rsCamera(realSenseResolution, realSenseFps)

    # Create a pipeline
    rs.createPipeline()

    # Start the pipeline
    rs.startPipeline()

    # Create the window
    window = getGUI(windowLocation[0], windowLocation[1], True)

    # Previous frame
    prevFrame = None

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Wait for the next frames from the camera
            frames = rs.grabFrames()

            # Get the color frame
            colorFrame, colorCamIntrinsics = rs.getColorFrame(frames)

            # Get the values from the GUI
            params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
                      'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
                      'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                      'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                      'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                      'windowWidth': windowWidth
                      }

            # Change brightness
            colorFrame = cv.convertScaleAbs(
                colorFrame, alpha=values['camAlpha'], beta=values['camBeta'])

            if prevFrame is None:
                prevFrame = np.copy(colorFrame)

            if (isSequentialSubtraction):
                frame, mask = processSequentialFrames(
                    prevFrame, colorFrame, True, params)
            else:
                frame, mask = processSingleFrame(colorFrame, True, params)

            # Show the frames
            frame = cv.imencode(".png", frame)[1].tobytes()
            window['Frames'].update(data=frame)

            # Save the previous frame
            prevFrame = np.copy(colorFrame)

    finally:
        # Stop the pipeline and close the windows
        rs.stopPipeline()
        cv.destroyAllWindows()
        print(
            f'Framework started! [RealSense Mono Setup - {monoSetupVariant}]')


# Run the program
main()
