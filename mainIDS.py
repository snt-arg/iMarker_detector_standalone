import cv2 as cv
import numpy as np
import PySimpleGUI as sg
from src.gui.addLabel import addLabel
from src.gui.guiElements import guiElements
from src.csr_sensors.sensors import sensorIDS
from src.csr_detector.process import processFrames
from config import preAligment, homographyMat, windowWidth


def main():
    print('Framework started! [iDS Cameras Setup]')

    # Create the window
    windowTitle, tabGroup, imageViewer = guiElements()
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=(800, 400))

    cap1 = sensorIDS.idsCamera(0)
    cap2 = sensorIDS.idsCamera(1)

    # cap.loadCameraParameters("src/parameters/cam1.cset")
    # cap2.loadCameraParameters("src/parameters/cam2.cset")
    cap2.setROI(480, 212, 976, 1094)
    cap1.setROI(520, 212, 976, 1094)

    cap1.syncAsMaster()
    cap2.syncAsSlave()

    cap1.startAquisition()
    cap2.startAquisition()

    cap1.setExposureTime(20000)
    cap2.setExposureTime(20000)

    while True:
        event, values = window.read(timeout=10)

        # End program if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        frame1 = cap1.getFrame()
        frame2 = cap2.getFrame()

        retL = False if (not np.any(frame1)) else True
        retR = False if (not np.any(frame2)) else True

        frameL = frame1
        frameR = frame2

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
            frameL, alpha=values['camAlpha'], beta=values['camBeta'])
        frameR = cv.convertScaleAbs(
            frameR, alpha=values['camAlpha'], beta=values['camBeta'])

        frameR = cv.flip(frameR, 1)

        frame = processFrames(frameL, frameR, retL, retR,
                              params)

        addLabel(frame, 5)

        frame = cv.imencode(".png", frame)[1].tobytes()
        window['Frames'].update(data=frame)

    window.close()
    cap1.closeLibrary()
    cap2.closeLibrary()
    print('Framework finished! [iDS Cameras Setup]')


# Run the program
main()
