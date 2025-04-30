"""
📝 'iMarker Detector (Standalone)' Software
    SPDX-FileCopyrightText: (2025) University of Luxembourg
    © 2025 University of Luxembourg
    Developed by: Ali TOURANI et al. at SnT / ARG.

'iMarker Detector (Standalone)' is licensed under the "SNT NON-COMMERCIAL" License.
You may not use this file except in compliance with the License.
"""

import io
import yaml
import pstats
import argparse
import cProfile


def startProfiler() -> cProfile.Profile:
    """
    Starts the profiler for performance analysis.

    Returns:
    ----------
    profile: cProfile.Profile
        The profiler object to be used for profiling the code.
    """
    # Create a profiler object and enable it
    profile = cProfile.Profile()
    profile.enable()
    print("\nProfiler started ...")
    # Return the profiler object
    return profile


def stopProfiler(profile: cProfile.Profile):
    """
    Stops the profiler and print the profiling results.

    Parameters:
    ----------
    profile: cProfile.Profile
        The profiler object to be used for profiling the code.
    """
    # Inform the user
    print("\nProfiler stopped. Check the results:")
    # Stop the profiler
    profile.disable()
    str = io.StringIO()
    stats = pstats.Stats(profile, stream=str).sort_stats(
        pstats.SortKey.TIME)
    stats.print_stats(35)
    # Print the profiling results
    print(str.getvalue())


def readConfig(configFilePath: str) -> dict:
    """
    Reads the configuration file available in the config folder.

    Parameters:
    ----------
    configFilePath: str
        The path to the configuration file.

    Returns:
    ----------
    config: dict
        The configuration dictionary containing the settings.
    """
    # Variables
    config = {}
    print(
        f"[Info] Reading the contents of the configuration file '{configFilePath}' ...")

    try:
        # Read configuration YAML from the given path
        with open(configFilePath, 'r') as file:
            config = yaml.safe_load(file)
        # Check if the config is empty
        if config is None:
            print(
                f"[Error] The configuration file '{configFilePath}' is empty. Exiting ...")
            exit(1)
        # Return the config
        return config
    # Handle exceptions
    except FileNotFoundError:
        print(
            f"[Error] The configuration file '{configFilePath}' was not found. Exiting ...")
        exit(1)
    except yaml.YAMLError as e:
        print(f"[Error] Error reading the configuration file: {e}")
        exit(1)
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")
        exit(1)


def argParser(mode: str) -> str:
    """
    Parse command line arguments and override the mode if provided.

    Parameters:
    ----------
    mode: str
        The mode to be used for the runner.

    Returns:
    ----------
    mode: str
        The mode to be used for the runner.
    """
    # Variables
    validModes = ["sv_offImg", "sv_offVid", "sv_offImgUV",
                  "dv_usb", "sv_usbUv", "sv_usbIr", "dv_ids", "sv_rs"]

    # Create an argument parser
    parser = argparse.ArgumentParser()

    # Add arguments to override config values
    parser.add_argument(
        '--mode', type=str, help="Override runner mode (sv_rs, dv_ids, dv_usb, sv_offVid, sv_offImg)")

    # New mode
    newMode = parser.parse_args().mode

    # Check if the mode is valid
    if newMode and newMode in validModes and newMode != mode:
        print(
            f'[Info] a new mode "{newMode}" is set using arguments, different from "{mode}" in the config file ...')
        mode = newMode

    # Check if the mode is valid
    if newMode and newMode not in validModes:
        print(
            f'[Warn] skipping the mode "{newMode}" set using arguments due to invalidity. Reading mode from the config file ...')

    # Return the parsed arguments
    return mode
