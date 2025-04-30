"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

from src.utils import argParser, readConfig
from src.singlevision_rs import runner_sv_rs
from src.dualvision_ids import runner_dv_ids
from src.dualvision_usb import runner_dv_usb
from src.singlevision_usb_ir import runner_sv_usb_ir
from src.singlevision_usb_uv import runner_sv_usb_uv
from src.singlevision_off_vid import runner_sv_off_vid
from src.singlevision_off_img import runner_sv_off_img
from src.singlevision_off_img_uv import runner_sv_off_img_uv


def main():
    # Read configurations from the config file
    config = readConfig('config/config.yaml')

    # Mode selection and overriding it if "--mode" is provided as argument
    mode = argParser(
        config['configs']['mode']['runner'])

    # Update the mode in the config
    config['configs']['mode']['runner'] = mode

    # Run the selected mode
    if mode == 'sv_rs':
        runner_sv_rs(config['configs'])
    elif mode == 'dv_ids':
        # Check if the user has installed `ids-peak` and `ids-peak-ipl` packages
        try:
            import ids_peak
            import ids_peak_ipl
            runner_dv_ids(config['configs'])
        except ImportError:
            print(
                '[Error] Please install the `ids-peak` and `ids-peak-ipl` packages to use the iDS camera runner.')
            return
    elif mode == 'dv_usb':
        runner_dv_usb(config['configs'])
    elif mode == 'sv_offVid':
        runner_sv_off_vid(config['configs'])
    elif mode == 'sv_offImg':
        runner_sv_off_img(config['configs'])
    elif mode == 'sv_offImgUV':
        runner_sv_off_img_uv(config['configs'])
    elif mode == 'sv_usbUv':
        runner_sv_usb_uv(config['configs'])
    elif mode == 'sv_usbIr':
        runner_sv_usb_ir(config['configs'])
    else:
        print(f'The selected mode "{mode}" is not valid. Exiting ...')


# Run the main function
if __name__ == '__main__':
    main()
