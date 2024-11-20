import cv2 as cv
from datetime import datetime


def resizeFrame(frame, widthThreshold=1000):
    """
    Resize the frame if the width exceeds the widthThreshold.

    Parameters
    ----------
    frame: numpy.ndarray
        Frame to resize.
    widthThreshold: int, optional (default=1000)
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


def fileNameGenerator(prefix: str, extension: str = 'png'):
    """
    Generate a unique file name with the given prefix and extension.

    Parameters
    ----------
    prefix: str
        Prefix for the file name.
    extension: str
        Extension for the file name.

    Returns
    -------
    fileName: str
        Unique file name.
    """
    fileName = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{fileName}_{prefix}.{extension}"


def frameSave(frame, prefix: str, extension: str = 'png'):
    """
    Save the frame with a unique file name.

    Parameters
    ----------
    frame: numpy.ndarray
        Frame to save.
    prefix: str
        Prefix for the file name.
    extension: str
        Extension for the file name.
    """
    # Prepare a unique file name and path
    fileName = fileNameGenerator(prefix, extension)
    filePath = 'outputs/' + fileName
    # Save the frame
    cv.imwrite(filePath, frame)
    print(f"- The current frame saved as {fileName}")


def hsvToRgbHex(h, s, v):
    """
    Convert HSV color to RGB hex color.

    Parameters
    ----------
    h: int
        Hue value.
    s: int
        Saturation value.
    v: int
        Value value.

    Returns
    -------
    hexColor: str
        RGB hex color.
    """
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h / 360, s / 255, v / 255)
    return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'
