import cv2 as cv
import numpy as np
from src.csr_sensors.sensors import sensorRealSense
from config import realSenseResolution, realSenseFps


def main():
    print('Framework started! [RealSense Mono Setup]')

    rs = sensorRealSense.rsCamera(realSenseResolution, realSenseFps)

    # Create a pipeline
    rs.createPipeline()

    # Start the pipeline
    rs.startPipeline()

    try:
        while True:
            # Wait for the next frames from the camera
            frames = rs.grabFrames()

            # Get the color frame
            colorFrame = rs.getColorFrame(frames)

            # Display the color image
            cv.imshow("RealSense Camera", colorFrame)

            # Exit the loop if the 'q' key is pressed
            if cv.waitKey(1) == ord('q'):
                break

    finally:
        # Stop the pipeline and close the windows
        rs.stopPipeline()
        cv.destroyAllWindows()
        print('Framework stopped! [RealSense Mono Setup]')


# Run the program
main()
