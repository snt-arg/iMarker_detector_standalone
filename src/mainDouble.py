import cv2 as cv
import PySimpleGUI as sg
from csr_detector.vision.addLabel import addLabel
from gui.guiElements import guiElements
from gui.config import ports, fpsBoost, flipImage
from csr_detector.vision.processFrames import processFrames
import csr_sensors.sensors.sensorUSB as usb


def main():
    windowTitle, tabGroup, imageViewer = guiElements()
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=(800, 400))

    capL = usb.createCameraObject(ports['lCam'])
    capR = usb.createCameraObject(ports['rCam'])

    if fpsBoost:
        capL.set(cv.CAP_PROP_FPS, 30.0)
        capR.set(cv.CAP_PROP_FPS, 30.0)

    while True:
        event, values = window.read(timeout=10)
        # End program if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        # Retrieve frames
        # Note: if each of the cameras not working, retX will be False
        retL, frameL = usb.grabImage(capL)
        retR, frameR = usb.grabImage(capR)
        # Get the values from the GUI
        guiValues = {'maxFeatures': values['MaxFeat'], 'goodMatchPercentage': values['MatchRate'],
                     'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
                     'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
                     'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
                     'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                     'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'], 'threshots': values['ThreshOts'],
                     'isMarkerLeftHanded': values['MarkerLeftHanded'],
                     }
        # Change brightness
        frameL = cv.convertScaleAbs(
            frameL, alpha=values['camAlpha'], beta=values['camBeta'])
        frameR = cv.convertScaleAbs(
            frameR, alpha=values['camAlpha'], beta=values['camBeta'])
        # Flip the right frame
        if (flipImage):
            frameR = cv.flip(frameR, 1)
        # Process frames
        frame = processFrames(frameL, frameR, retL, retR, guiValues)
        # Add text to the image
        # addLabel(frame, 5)
        # Show the frames
        frame = cv.imencode(".png", frame)[1].tobytes()
        window['Frames'].update(data=frame)

    capL.release()
    capR.release()
    window.close()
    print('Framework finished! [Simple Version]')


# Run the program
main()
