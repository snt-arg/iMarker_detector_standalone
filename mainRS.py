import cv2 as cv
import numpy as np
import PySimpleGUI as sg
from src.gui.guiElements import guiElements
from src.csr_sensors.sensors import sensorRealSense
from src.csr_detector.process import processMonoFrame
from config import realSenseResolution, realSenseFps, windowWidth, windowLocation


def main():
    print('Framework started! [RealSense Mono Setup]')

    # Create an object
    rs = sensorRealSense.rsCamera(realSenseResolution, realSenseFps)

    # Create a pipeline
    rs.createPipeline()

    # Start the pipeline
    rs.startPipeline()

    # Create the window
    windowTitle, tabGroup, imageViewer = guiElements(True)
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=windowLocation)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            # Wait for the next frames from the camera
            frames = rs.grabFrames()

            # Get the color frame
            colorFrame = rs.getColorFrame(frames)

            # Get the values from the GUI
            params = {'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
                      'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
                      'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
                      'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                      'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                      'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                      'windowWidth': windowWidth
                      }

            # Change brightness
            colorFrame = cv.convertScaleAbs(
                colorFrame, alpha=values['camAlpha'], beta=values['camBeta'])

            frame, mask = processMonoFrame(colorFrame, True, params)

            # Show the frames
            frame = cv.imencode(".png", frame)[1].tobytes()
            window['Frames'].update(data=frame)

    finally:
        # Stop the pipeline and close the windows
        rs.stopPipeline()
        cv.destroyAllWindows()
        print('Framework stopped! [RealSense Mono Setup]')


# Run the program
main()
