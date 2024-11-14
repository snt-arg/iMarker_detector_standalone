import cv2 as cv
import numpy as np


def getArucoDict(dictName: str):
    # Variables
    arucoDicts = {
        "DICT_4X4_50": cv.aruco.DICT_4X4_50,
        "DICT_4X4_100": cv.aruco.DICT_4X4_100,
        "DICT_4X4_250": cv.aruco.DICT_4X4_250,
        "DICT_4X4_1000": cv.aruco.DICT_4X4_1000,
        "DICT_5X5_50": cv.aruco.DICT_5X5_50,
        "DICT_5X5_100": cv.aruco.DICT_5X5_100,
        "DICT_5X5_250": cv.aruco.DICT_5X5_250,
        "DICT_5X5_1000": cv.aruco.DICT_5X5_1000,
        "DICT_6X6_50": cv.aruco.DICT_6X6_50,
        "DICT_6X6_100": cv.aruco.DICT_6X6_100,
        "DICT_6X6_250": cv.aruco.DICT_6X6_250,
        "DICT_6X6_1000": cv.aruco.DICT_6X6_1000,
        "DICT_7X7_50": cv.aruco.DICT_7X7_50,
        "DICT_7X7_100": cv.aruco.DICT_7X7_100,
        "DICT_7X7_250": cv.aruco.DICT_7X7_250,
        "DICT_7X7_1000": cv.aruco.DICT_7X7_1000,
        "DICT_ARUCO_ORIGINAL": cv.aruco.DICT_ARUCO_ORIGINAL,
        "DICT_APRILTAG_16h5": cv.aruco.DICT_APRILTAG_16h5,
        "DICT_APRILTAG_25h9": cv.aruco.DICT_APRILTAG_25h9,
        "DICT_APRILTAG_36h10": cv.aruco.DICT_APRILTAG_36h10,
        "DICT_APRILTAG_36h11": cv.aruco.DICT_APRILTAG_36h11,
    }

    # Get the corresponding dictionary constant
    dictConstant = arucoDicts.get(dictName, None)
    if dictConstant is None:
        raise ValueError(f"Aruco dictionary '{dictName}' is not recognized.")

    # Return the dictionary object
    return cv.aruco.getPredefinedDictionary(dictConstant)


def arucoMarkerDetector(frame, cameraMatrix, distCoeffs, arucoDict: str,
                        markerSize: float):
    """
    Detects the markers in the frame and returns the frame with the detected markers.

    Parameters
    ----------
    frame: numpy.ndarray
        Frame to detect the markers in.
    cameraMatrix: numpy.ndarray
        Camera matrix of the camera.
    distCoeffs: numpy.ndarray
        Distortion coefficients of the camera.
    arucoDict: str
        Aruco dictionary to use for marker detection.
    markerSize: float
        Size of the markers to detect in meters.        

    Returns
    -------
    frame: numpy.ndarray
        Frame with detected markers.
    """
    # Variables
    dictionary = getArucoDict(arucoDict)
    parameters = cv.aruco.DetectorParameters()
    rotationVecs, translationVecs = None, None

    # Detect the markers
    corners, ids, _ = cv.aruco.detectMarkers(
        frame, dictionary, parameters=parameters)

    # If markers are detected
    if ids is not None:
        # Draw the detected markers
        cv.aruco.drawDetectedMarkers(frame, corners, ids)

        # Estimate the pose of the markers
        rotationVecs, translationVecs, _ = cv.aruco.estimatePoseSingleMarkers(
            corners, markerSize, cameraMatrix, distCoeffs)

        # Draw the axes and overlay text for each marker
        for id in range(len(ids)):
            # Draw the axes
            cv.drawFrameAxes(frame, cameraMatrix, distCoeffs,
                             rotationVecs[id], translationVecs[id], length=0.1)
            # Calculate the distance (magnitude of the translation vector)
            distance = np.linalg.norm(translationVecs[id])
            # Prepare the text to display
            text = f"[Marker-id {ids[id][0]}, size: {markerSize*100}x{markerSize*100}cm, distance: {distance*100:.1f}cm]"
            # Set text position (near the top-left of the marker)
            textPosition = (5, frame.shape[0] - 10)
            # Add the text on the frame
            cv.putText(frame, text, textPosition, cv.FONT_HERSHEY_SIMPLEX,
                       0.3, (255, 150, 0), 1, cv.LINE_AA)

    # Return
    return frame
