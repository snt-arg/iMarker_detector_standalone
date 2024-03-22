import os
import cv2 as cv
from src.gui.utils import resizeFrame
from src.gui.guiElements import checkTerminateGUI, getGUI
from src.csr_detector.process import processSequentialFrames
from src.marker_detector.arucoMarkerDetector import arucoMarkerDetector
from config import windowWidth, windowLocation, imagesPath, imagesNames, arucoDict, arucoParams


def main():
    print('Framework started! [Offline Image Seq. Setup]')

    # Check if the images files exist
    image1Path = os.path.join(imagesPath, imagesNames[0])
    image2Path = os.path.join(imagesPath, imagesNames[1])
    if not os.path.exists(image1Path) or not os.path.exists(image2Path):
        print("At leaset one image does not exist!")
        return

    # Create the window
    window = getGUI(windowLocation[0], windowLocation[1], True)

    # Open the video file
    frame1 = cv.imread(image1Path)
    frame2 = cv.imread(image2Path)

    # Resize frames if necessary
    frame1 = resizeFrame(frame1)
    frame2 = resizeFrame(frame2)

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Get the values from the GUI
            params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
                      'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
                      'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                      'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                      'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                      'windowWidth': windowWidth, 'invertBinaryImage': values['invertBinaryImage'],
                      }

            prevFrame, currFrame, mask = processSequentialFrames(
                frame1, frame2, True, params)

            # Show the frames
            prevFrame = cv.imencode(".png", prevFrame)[1].tobytes()
            currFrame = cv.imencode(".png", currFrame)[1].tobytes()
            newMask = cv.imencode(".png", mask)[1].tobytes()
            window['FramesLeft'].update(data=prevFrame)
            window['FramesRight'].update(data=currFrame)
            window['FramesMask'].update(data=newMask)

            # ArUco marker detection
            detectedMarkers = arucoMarkerDetector(
                mask, arucoDict, arucoParams)
            detectedMarkers = cv.imencode(".png", detectedMarkers)[1].tobytes()
            window['FramesMarker'].update(data=detectedMarkers)

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print('Framework stopped! [Offline Image Seq. Setup]')


# Run the program
main()
