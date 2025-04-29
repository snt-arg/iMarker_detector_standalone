"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

from src.runner_rs import runner_rs
from src.runner_ids import runner_ids
from src.runner_usb import runner_usb
from src.runner_usb_uv import runner_usbUV
from src.utils import argParser, readConfig
from src.runner_offVid import runner_offVid
from src.runner_offImg import runner_offImg
from src.runner_offImg_uv import runner_offImgUV
from src.runner_sv_usb_ir import runner_singleVision_usbIR


def main():
    # Read configurations from the config file
    config = readConfig('config/config.yaml')

    # Mode selection and overriding it if "--mode" is provided as argument
    mode = argParser(
        config['configs']['mode']['runner'])

    # Update the mode in the config
    config['configs']['mode']['runner'] = mode

    # Run the selected mode
    if mode == 'rs':
        runner_rs(config['configs'])
    elif mode == 'ids':
        # Check if the user has installed `ids-peak` and `ids-peak-ipl` packages
        try:
            import ids_peak
            import ids_peak_ipl
            runner_ids(config['configs'])
        except ImportError:
            print(
                '[Error] Please install the `ids-peak` and `ids-peak-ipl` packages to use the iDS camera runner.')
            return
    elif mode == 'usb':
        runner_usb(config['configs'])
    elif mode == 'offvid':
        runner_offVid(config['configs'])
    elif mode == 'offimg':
        runner_offImg(config['configs'])
    elif mode == 'offimguv':
        runner_offImgUV(config['configs'])
    elif mode == 'usbuv':
        runner_usbUV(config['configs'])
    elif mode == 'sv_ir':
        runner_singleVision_usbIR(config['configs'])
    else:
        print(f'The selected mode "{mode}" is not valid. Exiting ...')


# Run the main function
if __name__ == '__main__':
    main()
