import cv2 as cv


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


def arucoMarkerDetector(frame, arucoDict: str):
    """
    Detects the markers in the frame and returns the frame with the detected markers.

    Parameters
    ----------
    frame: numpy.ndarray
        Frame to detect the markers in.
    arucoDict: str
        Aruco dictionary to use for marker detection.
    arucoParams: cv.aruco_DetectorParameters
        Aruco parameters to use for marker detection.

    Returns
    -------
    numpy.ndarray
        Frame with detected markers.
    """
    # Variables
    dictionary = getArucoDict(arucoDict)
    parameters = cv.aruco.DetectorParameters()
    # Detect the markers
    corners, ids, _ = cv.aruco.detectMarkers(
        frame, dictionary, parameters=parameters)
    # Draw the detected markers
    if ids is not None:
        cv.aruco.drawDetectedMarkers(frame, corners, ids)
    return frame
