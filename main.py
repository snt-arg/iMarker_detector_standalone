import yaml
import argparse
from src.runner_rs import runner_rs
from src.runner_ids import runner_ids
from src.runner_usb import runner_usb
from src.runner_usb_uv import runner_usbUV
from src.runner_offVid import runner_offVid
from src.runner_offImg import runner_offImg
from src.runner_offImg_uv import runner_offImgUV


def readConfig(config):
    config = {}
    # Read config YAML from file
    with open('config/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    # Return the config
    return config


def argParser(mode: str):
    # Variables
    validModes = ["offimg", "offvid", "offimguv", "usb", "usbuv", "ids", "rs"]
    # Create an argument parser
    parser = argparse.ArgumentParser()
    # Add arguments to override config values
    parser.add_argument(
        '--mode', type=str, help="Override runner mode (rs, ids, usb, offvid, offimg)")
    # New mode
    newMode = parser.parse_args().mode
    # Check if the mode is valid
    if newMode and newMode in validModes and newMode != mode:
        print(
            f'[Info] a new mode "{newMode}" is set using arguments, which is different from "{mode}" in the config file ...')
        mode = newMode
    # Check if the mode is valid
    if newMode and newMode not in validModes:
        print(
            f'[Warn] skipping the mode "{newMode}" set using arguments due to invalidity. Reading mode from the config file ...')
    # Return the parsed arguments
    return mode


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
    else:
        print(f'The selected mode "{mode}" is not valid. Exiting ...')


# Run the main function
if __name__ == '__main__':
    main()
