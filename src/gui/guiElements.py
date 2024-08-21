import PySimpleGUI as sg


def guiElements(cfg: dict, singleCamera: bool = False):
    """
    Defines GUI elements for controlling the system (single and two-camera setups)

    Parameters
    -------
    cfg: dict
        The dictionary containing the system parameters
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
    # Get parameters
    cfgGui = cfg['gui']
    cfgMode = cfg['mode']
    cfgAlgortihm = cfg['algorithm']
    cfgUsbCam = cfg['sensor']['usbCam']
    cfgSensor = cfg['sensor']['general']

    # Get further parameters
    cfgProc = cfgAlgortihm['process']
    cfgAlignment = cfgProc['alignment']
    cfgPostproc = cfgAlgortihm['postprocess']
    thresholdSize = cfgPostproc['threshold']['size']
    thresholdMethod = cfgPostproc['threshold']['method']

    # Preparation of the GUI elements
    isRChannel = True if (cfgProc['channel'] == 'r') else False
    isGChannel = True if (cfgProc['channel'] == 'g') else False
    isBChannel = True if (cfgProc['channel'] == 'b') else False
    isAllChannels = True if (cfgProc['channel'] == 'all') else False
    isThreshOts = True if (thresholdMethod == 'otsu') else False
    isThreshBoth = True if (thresholdMethod == 'both') else False
    isThreshBin = True if (thresholdMethod == 'binary') else False

    # Define various modes
    isUsbCam = True if cfgMode['runner'] == 'usb' else False
    isIdsCam = True if cfgMode['runner'] == 'ids' else False
    isRealSense = True if cfgMode['runner'] == 'rs' else False
    isOffImg = True if cfgMode['runner'] == 'offimg' else False
    isOffVid = True if cfgMode['runner'] == 'offvid' else False
    isSequential = True if cfgMode['sequentialSubtraction'] else False

    # Preparing the title
    setupVariant = "Sequential Subtraction" if isSequential else "Masking"
    windowTitle = f"iMarker Readout - {'Single' if singleCamera else 'Double'} Vision Setup"
    windowTitle += f" [{setupVariant}]" if isOffImg or isOffVid or isRealSense else ""

    # Preparing sensor-related GUI elements
    boostFrameRate = [sg.Text('Boosting frame-rate?', size=cfgGui['labelSize']),
                      sg.Text(
        f'{"Enabled" if cfgSensor["fpsBoost"] else "Disabled"}')] if isUsbCam else []

    # Adding GUI elements
    tabGeneral = [boostFrameRate,
                  [sg.Text('Subtraction order:', size=cfgGui['labelSize']),
                   sg.Checkbox(
                       '(uncheck to reverse)', default=cfgProc['subtractRL'], key="SubtractionOrder")],
                  [sg.Text('Invert binary image:', size=cfgGui['labelSize']),
                   sg.Checkbox('(check to invert)', default=cfgPostproc['invertBinary'], key="invertBinaryImage")],
                  [sg.Text('Color-range filter:', size=cfgGui['labelSize']),
                   sg.Radio("All", "Channels",
                            key='AChannels', default=isAllChannels),
                   sg.Radio("Red", "Channels", key='RChannel',
                            default=isRChannel),
                   sg.Radio("Green", "Channels",
                            key='GChannel', default=isGChannel),
                   sg.Radio("Blue", "Channels",
                            key='BChannel', default=isBChannel)],
                  [sg.Text("Brightness & contrast:", size=cfgGui['labelSize']),
                   sg.Slider((1.0, 15.0), cfgSensor['brightness']['alpha'], .1, orientation="h", size=(
                       50, 15), key="camAlpha"),
                   sg.Slider((0, 50), cfgSensor['brightness']['beta'], 1, orientation="h", size=(50, 15), key="camBeta")]]

    tabAlignment = [
        [sg.Text('Max. features:', size=cfgGui['labelSize']),
         sg.Slider((10, 1000), cfgAlignment['maxFeatures'], 10, orientation="h", size=cfgGui['sliderSize'], key="MaxFeat")],
        [sg.Text('Matching rate:', size=cfgGui['labelSize']),
         sg.Slider(
            (0, 1), cfgAlignment['matchRate'], .1, orientation="h", size=cfgGui['sliderSize'], key="MatchRate")],
        [sg.Text('Circular mask:', size=cfgGui['labelSize']), sg.Slider((0, 1), cfgUsbCam['maskSize'], .01, orientation="h", size=cfgGui['sliderSize'], key="CircMask"),
         sg.Checkbox('Enable Circular Mask', default=cfgUsbCam['enableMask'], key="CircMaskEnable")]]

    tabPosProcessing = [
        [sg.Text('Thresholding method:', size=cfgGui['labelSize']),
         sg.Radio("Binary thresholding", "ThreshMeth",
                  key='ThreshBin', default=isThreshBin),
         sg.Radio("Otsu algorithm", "ThreshMeth",
                  key='ThreshOts', default=isThreshOts),
         sg.Radio("Both", "ThreshMeth", key='ThreshBoth', default=isThreshBoth)],
        [sg.Text('Thresholding value:', size=cfgGui['labelSize']),
         sg.Slider((1, 255), thresholdSize, 1, orientation="h", size=cfgGui['sliderSize'], key="Threshold")],
        [sg.Text('Erosion kernel size (noise removal):', size=cfgGui['labelSize']),
         sg.Slider((1, 50), cfgPostproc['erosionKernelSize'], 1, orientation="h", size=cfgGui['sliderSize'], key="Erosion")],
        [sg.Text('Gaussian kernel size (smoothing):', size=cfgGui['labelSize']),
         sg.Slider((1, 49), cfgPostproc['gaussianKernelSize'], 2, orientation="h", size=cfgGui['sliderSize'], key="Gaussian")]]

    # Define tab group values based on camera setup
    groups = [[sg.Tab('General Settings', tabGeneral),
               sg.Tab('Post-Processing', tabPosProcessing)]] if singleCamera else [[sg.Tab('General Settings', tabGeneral), sg.Tab('Alignment Configurations', tabAlignment),
                                                                                    sg.Tab('Post-Processing', tabPosProcessing)]]
    tabGroup = [[sg.Image(filename="./src/logo.png",  key="LogoHolder"),
                 sg.TabGroup(groups, tab_location='centertop', expand_x=True,
                             title_color='dark slate grey', selected_background_color='dark orange', pad=10)]]

    # Define image viewer values based on camera setup
    imageViewerL = [[sg.Image(filename="", key="FramesLeft")]]
    imageViewerR = [[sg.Image(filename="", key="FramesRight")]]
    imageViewerMask = [[sg.Image(filename="", key="FramesMask")]]
    imageViewerMain = [[sg.Image(filename="", key="FramesMain")]]
    imageViewerMarker = [[sg.Image(filename="", key="FramesMarker")]]
    imageViewerMaskApplied = [[sg.Image(filename="", key="FramesMaskApplied")]]

    # Check the camera setup
    if singleCamera:
        if isSequential:
            tabImages = [
                [sg.Tab('Previous Frame', imageViewerL),
                 sg.Tab('Current Frame', imageViewerR),
                 sg.Tab('Mask Frame', imageViewerMask),
                 sg.Tab('Mask Applied', imageViewerMaskApplied),
                 sg.Tab('Detected Markers', imageViewerMarker)]
            ]
        else:
            tabImages = [
                        [sg.Tab('Raw Frame', imageViewerMain),
                         sg.Tab('Mask Frame', imageViewerMask),
                         sg.Tab('Mask Applied', imageViewerMaskApplied),
                         sg.Tab('Detected Markers', imageViewerMarker)]
            ]
    else:
        tabImages = [
            [sg.Tab('Raw Frame Left', imageViewerL),
             sg.Tab('Raw Frame Right', imageViewerR),
             sg.Tab('Mask Frame', imageViewerMask),
             sg.Tab('Detected Markers', imageViewerMarker)]
        ]

    tabImageGroup = [[sg.TabGroup(tabImages, tab_location='centertop', expand_x=True,
                                  title_color='dark slate grey', selected_background_color='dark orange', pad=10)]]

    tabFooter = [[sg.Text('© 2022-2024 - TRANSCEND Project - University of Luxembourg', size=cfgGui['labelSize']),
                  sg.Push(),  # Pushing the following element to the rightmost
                  sg.Button('Save the Current Frame', key="Record",
                            size=cfgGui['buttonSize'], button_color=('white', 'green'))]]

    # Return to GUI creator
    return windowTitle, tabGroup, tabImageGroup, tabFooter


def getGUI(config: dict, singleCamera: bool = False):
    """
    Creates a set of GUI elements and send it back

    Parameters
    -------
    config: dict
        The dictionary containing various parameters

    Returns
    -------
    window: Window
        The window containing all the GUI
    """
    # Get parameters
    xLoc, yLoc = config['gui']['windowLocation']
    # Create the window
    windowTitle, tabGroup, tabImages, tabFooter = guiElements(
        config, singleCamera)
    window = sg.Window(
        windowTitle, [tabGroup, tabImages, tabFooter], location=(xLoc, yLoc), resizable=False)
    # Return to the called function
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
