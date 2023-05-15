import cv2 as cv
import numpy as np
from csr_detector.vision.processFrames import processFrames
from csr_detector.vision.addLabel import addLabel
import PySimpleGUI as sg
from gui.guiElements import guiElements
from csr_sensors.sensors import sensorIDS


def main():
    # Creating log file
    print('Framework started! [iDS Version]')
    # Create the window
    windowTitle, tabGroup, imageViewer = guiElements()
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=(800, 400))

    cap = sensorIDS.idsCamera(0)
    cap2 = sensorIDS.idsCamera(1)

    cap.loadCameraParameters("src/parameters/cam1.cset")
    cap.loadCameraParameters("src/parameters/cam2.cset")

    cap.syncAsMaster()
    cap2.syncAsSlave()

    cap.startAquisition()
    cap2.startAquisition()

    cap.setExposureTime(20000)
    cap2.setExposureTime(20000)

    while True:
        event, values = window.read(timeout=10)
        # End program if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        frame = cap.getFrame()
        frame2 = cap2.getFrame()

        if (not np.any(frame)):
            retL = False  # improvised
        else:
            retL = True
        frameL = frame

        if (not np.any(frame2)):
            retR = False  # improvised
        else:
            retR = True  # improvised

        frameR = frame2

        guiValues = {'maxFeatures': values['MaxFeat'], 'goodMatchPercentage': values['MatchRate'],
                     'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
                     'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
                     'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
                     'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                     'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'], 'threshots': values['ThreshOts'],
                     'isMarkerLeftHanded': values['MarkerLeftHanded'],
                     }

        frameL = cv.convertScaleAbs(
            frameL, alpha=values['camAlpha'], beta=values['camBeta'])
        frameR = cv.convertScaleAbs(
            frameR, alpha=values['camAlpha'], beta=values['camBeta'])

        frameR = cv.flip(frameR, 1)

        frame = processFrames(frameL, frameR, retL, retR,
                              guiValues)

        addLabel(frame, 5)

        frame = cv.imencode(".png", frame)[1].tobytes()
        window['Frames'].update(data=frame)

    window.close()
    cap.closeLibrary()
    cap2.closeLibrary()
    print('Application has been closed!')


# Run the program
main()
