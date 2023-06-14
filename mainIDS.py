import cv2 as cv
import numpy as np
import PySimpleGUI as sg
from src.gui.addLabel import addLabel
from src.gui.guiElements import guiElements
from src.csr_sensors.sensors import sensorIDS
from src.csr_detector.process import processFrames
from config import roiDimension, exposureTime, windowLocation
from config import preAligment, homographyMat, windowWidth, sensorProjectRoot


def main():
    print('Framework started! [iDS Cameras Setup]')

    # Create the window
    windowTitle, tabGroup, imageViewer = guiElements()
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=windowLocation)

    cap1 = sensorIDS.idsCamera(0)
    cap2 = sensorIDS.idsCamera(1)

    cap1.getCalibrationConfig(sensorProjectRoot, 'cam1')
    cap2.getCalibrationConfig(sensorProjectRoot, 'cam2')

    cap1.setROI(roiDimension['cap1']['x'], roiDimension['cap1']
                ['y'], roiDimension['cap1']['width'], roiDimension['cap1']['height'])
    cap2.setROI(roiDimension['cap2']['x'], roiDimension['cap2']
                ['y'], roiDimension['cap2']['width'], roiDimension['cap2']['height'])

    cap1.syncAsMaster()
    cap2.syncAsSlave()

    cap1.startAquisition()
    cap2.startAquisition()

    cap1.setExposureTime(exposureTime)
    cap2.setExposureTime(exposureTime)

    while True:
        event, values = window.read(timeout=10)

        # End program if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        frame1 = cap1.getFrame()
        frame2 = cap2.getFrame()

        retL = False if (not np.any(frame1)) else True
        retR = False if (not np.any(frame2)) else True

        # Get the values from the GUI
        params = {'maxFeatures': values['MaxFeat'], 'goodMatchPercentage': values['MatchRate'],
                  'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
                  'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
                  'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
                  'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                  'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'], 'threshots': values['ThreshOts'],
                  'isMarkerLeftHanded': values['MarkerLeftHanded'],
                  'preAligment': preAligment, 'homographyMat': homographyMat, 'windowWidth': windowWidth
                  }

        frameL = cv.convertScaleAbs(
            frame1, alpha=values['camAlpha'], beta=values['camBeta'])
        frameR = cv.convertScaleAbs(
            frame2, alpha=values['camAlpha'], beta=values['camBeta'])

        frameR = cv.flip(frameR, 1)

        # Process frames
        frame, mask = processFrames(frameL, frameR, retL, retR,
                                    params)

        # Add text to the image
        # addLabel(frame, 5)

        # Show the frames
        frame = cv.imencode(".png", frame)[1].tobytes()
        window['Frames'].update(data=frame)

    window.close()
    cap1.closeLibrary()
    cap2.closeLibrary()
    print('Framework finished! [iDS Cameras Setup]')


# Run the program
main()
