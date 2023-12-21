import os
import cv2 as cv
import PySimpleGUI as sg
from src.gui.guiElements import guiElements
from src.csr_detector.process import processSequentialFrames
from config import windowWidth, windowLocation, imagesPath, imagesNames


def main():
    print('Framework started! [Offline Image Seq. Setup]')

    # Check if the images files exist
    image1Path = os.path.join(imagesPath, imagesNames[0])
    image2Path = os.path.join(imagesPath, imagesNames[1])
    if not os.path.exists(image1Path) or not os.path.exists(image2Path):
        print("At leaset one image does not exist!")
        return

    # Create the window
    # screenResolution = sg.Window.get_screen_size()
    windowTitle, tabGroup, imageViewer = guiElements(True)
    window = sg.Window(
        windowTitle, [tabGroup, imageViewer], location=windowLocation, resizable=True)

    # Open the video file
    frame1 = cv.imread(image1Path)
    frame2 = cv.imread(image2Path)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            # Get the values from the GUI
            params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
                      'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
                      'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                      'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                      'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                      'windowWidth': windowWidth
                      }

            frame, mask = processSequentialFrames(
                frame1, frame2, True, params)

            # Resize the frame while keeping the aspect ratio to fit the height of the window
            ratio = windowWidth / frame.shape[1]
            dim = (windowWidth, int(frame.shape[0] * ratio))
            frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

            # Show the frames
            frame = cv.imencode(".png", frame)[1].tobytes()
            window['Frames'].update(data=frame)

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print('Framework stopped! [Offline Image Seq. Setup]')


# Run the program
main()
