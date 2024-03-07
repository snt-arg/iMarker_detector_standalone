import cv2 as cv


def arucoMarkerDetector(frame, arucoDict, arucoParams):
    """
    Detects the markers in the frame and returns the frame with the detected markers.

    Parameters
    ----------
    frame: numpy.ndarray
        Frame to detect the markers in.
    arucoDict: cv.aruco_Dictionary
        Aruco dictionary to use for marker detection.
    arucoParams: cv.aruco_DetectorParameters
        Aruco parameters to use for marker detection.

    Returns
    -------
    numpy.ndarray
        Frame with detected markers.
    """
    # Detect the markers
    corners, ids, _ = cv.aruco.detectMarkers(
        frame, arucoDict)
    # Draw the detected markers
    if ids is not None:
        cv.aruco.drawDetectedMarkers(frame, corners, ids)
    return frame
