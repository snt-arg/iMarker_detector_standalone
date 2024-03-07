import os
import cv2 as cv
import numpy as np
from src.gui.guiElements import getGUI, checkTerminateGUI
from config import windowWidth, windowLocation, videoPath
from src.csr_detector.process import processSequentialFrames


def main():
    print('Framework started! [Offline Video Seq. Setup]')

    # Check if the video file exists
    if not os.path.exists(videoPath):
        print("Video file does not exist!")
        return

    # Create the window
    window = getGUI(windowLocation[0], windowLocation[1], True)

    # Open the video file
    cap = cv.VideoCapture(videoPath)

    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    # Previous frame
    prevFrame = None

    try:
        while True:
            event, values = window.read(timeout=10)

            # End program if user closes window
            if checkTerminateGUI(event):
                break

            # Retrieve frames
            ret, currFrame = cap.read()

            # Break out of the loop if the video is finished
            if not ret:
                break

            # Get the values from the GUI
            params = {'threshold': values['Threshold'], 'erosionKernel': values['Erosion'],
                      'gaussianKernel': values['Gaussian'], 'allChannels': values['AChannels'],
                      'rChannel': values['RChannel'], 'gChannel': values['GChannel'], 'bChannel': values['BChannel'],
                      'threshboth': values['ThreshBoth'], 'threshbin': values['ThreshBin'],
                      'threshots': values['ThreshOts'], 'isMarkerLeftHanded': values['MarkerLeftHanded'],
                      'windowWidth': windowWidth, 'invertBinaryImage': values['invertBinaryImage'],
                      }

            # Change brightness
            currFrame = cv.convertScaleAbs(
                currFrame, alpha=values['camAlpha'], beta=values['camBeta'])

            # Rotate the frame 180 degrees [TODO: add to config.py]
            # currFrame = cv.rotate(currFrame, cv.ROTATE_180)

            if prevFrame is None:
                prevFrame = np.copy(currFrame)

            prevFrame, currFrame, mask = processSequentialFrames(
                prevFrame, currFrame, True, params)

            # Resize the frame while keeping the aspect ratio to fit the height of the window
            # ratio = windowWidth / frame.shape[1] / 2
            # dim = (windowWidth, int(frame.shape[0] * ratio))
            # frame = cv.resize(frame, dim, interpolation=cv.INTER_AREA)

            # Show the frames
            prevFrame = cv.imencode(".png", prevFrame)[1].tobytes()
            currFrame = cv.imencode(".png", currFrame)[1].tobytes()
            mask = cv.imencode(".png", mask)[1].tobytes()
            window['FramesLeft'].update(data=prevFrame)
            window['FramesRight'].update(data=currFrame)
            window['FramesMask'].update(data=mask)

            # Save the previous frame
            prevFrame = np.copy(currFrame)

    finally:
        # Stop the pipeline and close the windows
        cv.destroyAllWindows()
        print('Framework stopped! [Offline Video Seq. Setup]')


# Run the program
main()
