import cv2 as cv


def resizeFrame(frame, widthThreshold=1000):
    """
    Resize the frame if the width exceeds the widthThreshold.

    Parameters
    ----------
    frame : numpy.ndarray
        Frame to resize.
    widthThreshold : int, optional (default=1000)
        Width threshold to resize the frame.

    Returns
    -------
    frame: numpy.ndarray
        Resized frame.
    """
    # Get original frame dimensions
    height, width, _ = frame.shape

    # Resize only if width exceeds widthThreshold pixels
    if width > widthThreshold:
        # Calculate the scaling factor to make width widthThreshold pixels
        scaleFactor = widthThreshold / width
        newWidth = int(width * scaleFactor)
        newHeight = int(height * scaleFactor)

        # Resize the frame
        resizedFrame = cv.resize(frame, (newWidth, newHeight))
        return resizedFrame
    else:
        return frame
