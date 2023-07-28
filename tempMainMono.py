import cv2 as cv
from config import ports, fpsBoost
import src.csr_sensors.sensors.sensorUSB as usb


def main():
    cap = usb.createCameraObject(ports['lCam'])

    if fpsBoost:
        cap.set(cv.CAP_PROP_FPS, 30.0)

    while True:
        # Retrieve frames
        ret, frame = usb.grabImage(cap)

        # Check if the frame is successfully read
        if not ret:
            print("Failed to read a frame from the camera.")
            break

        # Change brightness
        frame = cv.convertScaleAbs(
            frame, alpha=2.0, beta=0.0)

        # Convert the image to grayscale
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Thresholding
        _, mask = cv.threshold(frame, 5, 255,
                               cv.THRESH_BINARY)

        # Show the frames
        cv.imshow("USB Camera Feed", mask)

        # Exit the loop if the 'q' key is pressed
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()


# Run the program
main()
