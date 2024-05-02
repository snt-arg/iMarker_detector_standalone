import PySimpleGUI as sg
from config import enableCircularROI, channel, leftHanded
from config import fpsBoost, brightness, labelSize, sliderSize
from config import maxFeatures, goodMatchPercentage, circlularMaskCoverage, invertBinaryImage
from config import threshold, erodeKernelSize, gaussianBlurKernelSize, thresholdMethod, isSequentialSubtraction


def guiElements(singleCamera: bool = False):
    """
    Defines GUI elements for controlling the system (single and two-camera setups)

    Parameters
    -------
    singleCamera: bool
        The bool to set the command of single/double camera setup

    Returns
    -------
    windowTitle: str
        The name of the window to be shown
    tabGroup: list
        The list of tabs and their contents attached to the window
    imageViewer: list
        An image placeholder to show the outputs of the cameras
    """
    # Preparation
    isRChannel = True if (channel == 'r') else False
    isGChannel = True if (channel == 'g') else False
    isBChannel = True if (channel == 'b') else False
    isAllChannels = True if (channel == 'all') else False
    isThreshOts = True if (thresholdMethod == 'otsu') else False
    isThreshBoth = True if (thresholdMethod == 'both') else False
    isThreshBin = True if (thresholdMethod == 'binary') else False
    # Adding GUI elements
    windowTitle = f"CSR Marker Readout - {'Single' if singleCamera else 'Double'} Camera Setup"
    tabGeneral = [[sg.Text('Frame-rate:', size=labelSize), sg.Text('-' + f' fps {"(boosted)" if fpsBoost else "(normal)"}')],
                  [sg.Text('Marker Properties:', size=labelSize), sg.Checkbox('Left-handed?',
                                                                              default=leftHanded, key="MarkerLeftHanded")],
                  [sg.Text('Color-range Filter:', size=labelSize), sg.Radio("All Channels", "Channels", key='AChannels', default=isAllChannels),
                   sg.Radio("Red", "Channels",
                            key='RChannel', default=isRChannel),
                   sg.Radio("Green", "Channels",
                            key='GChannel', default=isGChannel),
                   sg.Radio("Blue", "Channels",
                            key='BChannel', default=isBChannel)],
                  [sg.Text("Camera brightness/contrast:", size=labelSize), sg.Slider((1.0, 15.0), brightness['alpha'], .1, orientation="h", size=(50, 15), key="camAlpha"),
                   sg.Slider((0, 50), brightness['beta'], 1, orientation="h", size=(50, 15), key="camBeta")]]
    tabAlignment = [
        [sg.Text('Max. features:', size=labelSize), sg.Slider(
            (10, 1000), maxFeatures, 10, orientation="h", size=sliderSize, key="MaxFeat")],
        [sg.Text('Matching rate:', size=labelSize), sg.Slider(
            (0, 1), goodMatchPercentage, .1, orientation="h", size=sliderSize, key="MatchRate")],
        [sg.Text('Circular mask:', size=labelSize), sg.Slider((0, 1), circlularMaskCoverage, .01, orientation="h", size=sliderSize, key="CircMask"),
         sg.Checkbox('Enable Circular Mask', default=enableCircularROI, key="CircMaskEnable")]]
    tabPosProcessing = [
        [sg.Text('Threshold Method:', size=labelSize),
         sg.Radio("Binary", "ThreshMeth",
                  key='ThreshBin', default=isThreshBin),
         sg.Radio("Otsu", "ThreshMeth",
                  key='ThreshOts', default=isThreshOts),
         sg.Radio("Binary+Otsu", "ThreshMeth", key='ThreshBoth', default=isThreshBoth)],
        [sg.Text('Threshold:', size=labelSize), sg.Slider(
            (1, 255), threshold, 1, orientation="h", size=sliderSize, key="Threshold")],
        [sg.Text('Invert the Binary Image?', size=labelSize), sg.Checkbox('(Check for Yes)',
                                                                          default=invertBinaryImage, key="invertBinaryImage")],
        [sg.Text('Erosion kernel:', size=labelSize), sg.Slider(
            (1, 50), erodeKernelSize, 1, orientation="h", size=sliderSize, key="Erosion")],
        [sg.Text('Gaussian kernel:', size=labelSize), sg.Slider((1, 49), gaussianBlurKernelSize, 2, orientation="h", size=sliderSize, key="Gaussian")]]

    # Define tab group values based on camera setup
    groups = [[sg.Tab('General Settings', tabGeneral), sg.Tab('Post-Processing', tabPosProcessing)]] if singleCamera else [[sg.Tab('General Settings', tabGeneral), sg.Tab('Alignment Configurations', tabAlignment),
                                                                                                                            sg.Tab('Post-Processing', tabPosProcessing)]]

    tabGroup = [[sg.Image(filename="./src/logo.png",  key="LogoHolder"),
                 sg.TabGroup(groups, tab_location='centertop', expand_x=True,
                             title_color='dark slate grey', selected_background_color='dark orange', pad=10)]]
    # Define image viewer values based on camera setup
    imageViewerMain = [[sg.Image(filename="", key="FramesMain")]]
    imageViewerLeft = [[sg.Image(filename="", key="FramesLeft")]]
    imageViewerRight = [[sg.Image(filename="", key="FramesRight")]]
    imageViewerMask = [[sg.Image(filename="", key="FramesMask")]]
    imageViewerMarker = [[sg.Image(filename="", key="FramesMarker")]]
    imageViewerMaskApplied = [[sg.Image(filename="", key="FramesMaskApplied")]]
    if singleCamera:
        if isSequentialSubtraction:
            tabImages = [
                [sg.Tab('Previous Frame', imageViewerLeft),
                 sg.Tab('Current Frame', imageViewerRight),
                 sg.Tab('Mask Frame', imageViewerMask),
                 sg.Tab('Mask Applied Frame', imageViewerMaskApplied),
                 sg.Tab('Detected Markers', imageViewerMarker)]
            ]
        else:
            tabImages = [
                        [sg.Tab('Raw Frame', imageViewerMain),
                         sg.Tab('Mask Frame', imageViewerMask),
                         sg.Tab('Mask Applied Frame', imageViewerMaskApplied),
                         sg.Tab('Detected Markers', imageViewerMarker)]
            ]
    else:
        tabImages = [
            [sg.Tab('Raw Frame Left', imageViewerLeft)],
            [sg.Tab('Raw Frame Right', imageViewerRight)],
            [sg.Tab('Mask Frame', imageViewerMask)],
            sg.Tab('Mask Applied Frame', imageViewerMaskApplied),
            [sg.Tab('Detected Markers', imageViewerMarker)]
        ]
    tabImageGroup = [[sg.TabGroup(tabImages, tab_location='centertop', expand_x=True,
                                  title_color='dark slate grey', selected_background_color='dark orange', pad=10)]]
    # Return to GUI creator
    return windowTitle, tabGroup, tabImageGroup


def getGUI(xLoc: int = 800, yLoc: int = 400, singleCamera: bool = False):
    """
    Creates a set of GUI elements and send it back

    Parameters
    -------
    xLoc: int
        The horizontal location of GUI window
    yLoc: int
        The vertical location of GUI window

    Returns
    -------
    window: Window
        The window containing all the GUI
    """
    windowTitle, tabGroup, tabImages = guiElements(singleCamera)
    window = sg.Window(
        windowTitle, [tabGroup, tabImages], location=(xLoc, yLoc), resizable=True)
    return window


def checkTerminateGUI(event):
    """
    Creates a set of GUI elements and send it back

    Parameters
    -------
    window: Window
        The window containing all the GUI

    Returns
    -------
    stopGUI: bool
        The bool to set the command of stop/continue GUI
    """
    stopGUI = False
    # End program if user closes window
    if event == "Exit" or event == sg.WIN_CLOSED:
        stopGUI = True
    # Return to the called
    return stopGUI
