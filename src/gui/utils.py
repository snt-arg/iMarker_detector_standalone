"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

import colorsys
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


def hsvToRgbTuple(hsvValue: list):
    """
    Convert HSV tuple to RGB tuple.

    Parameters
    ----------
    hsvValue: list
        HSV value as a list of three integers [H, S, V].

    Returns
    -------
    rgbTuple: tuple
        RGB tuple.
    """
    # Variables
    h, s, v = hsvValue
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s / 255.0, v / 255.0)

    # Convert to 0-255 range
    rgbTuple = (int(r * 255), int(g * 255), int(b * 255), 1.0)
    return rgbTuple


def rgbToHsvTuple(rgbValue: list):
    """
    Convert RGB tuple to HSV tuple.

    Parameters
    ----------
    rgbValue: list
        RGB value as a list of three integers [R, G, B].

    Returns
    -------
    hsvTuple: tuple
        HSV tuple.
    """
    # Variables
    r, g, b, a = rgbValue
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Convert to 0-255 range
    hsvTuple = (int(h * 360), int(s * 255), int(v * 255))
    return hsvTuple
