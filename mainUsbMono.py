import cv2 as cv
import PySimpleGUI as sg
from src.gui.guiElements import guiElements
import src.csr_sensors.sensors.sensorUSB as usb
from src.csr_detector.process import processMonoFrame
from config import ports, fpsBoost, windowWidth, windowLocation


def main():
    print('Framework started! [USB Camera Mono Setup]')

    # Create the window
    windowTitle, tabGroup, imageViewer = guiElements()
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=windowLocation)

    cap = usb.createCameraObject(ports['rCam'])

    if fpsBoost:
        cap.set(cv.CAP_PROP_FPS, 30.0)

    while True:
        event, values = window.read(timeout=10)

        # End program if user closes window
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Retrieve frames
        ret, frame = usb.grabImage(cap)

        # Get the values from the GUI
        params = {'circlularMaskCoverage': values['CircMask'], 'threshold': values['Threshold'],
                  'erosionKernel': values['Erosion'], 'gaussianKernel': values['Gaussian'],
                  'enableCircularMask': values['CircMaskEnable'], 'allChannels': values['AChannels'],
                  'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                  'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                  'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                  'windowWidth': windowWidth
                  }

        # Check if the frame is successfully read
        if not ret:
            print("Failed to read a frame from the camera.")
            break

        # Change brightness
        frame = cv.convertScaleAbs(
            frame, alpha=values['camAlpha'], beta=values['camBeta'])

        # Process frames
        frame, mask = processMonoFrame(frame, ret, params)

        # Show the frames
        frame = cv.imencode(".png", frame)[1].tobytes()
        window['Frames'].update(data=frame)

    cap.release()
    window.close()
    print('Framework finished! [USB Camera Mono Setup]')


# Run the program
main()
