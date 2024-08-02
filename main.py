import yaml
from src.mainIDS import mainIDS
from src.mainUSB import mainUSB
from src.mainRS import mainRealSense
from src.mainOffline_video import mainOfflineVideo
from src.mainOffline_image import mainOfflineImage


def readConfig(config):
    config = {}
    # Read config YAML from file
    with open('config/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    # Return the config
    return config


def main():
    # Read the config
    config = readConfig('config/config.yaml')
    # Mode selection
    mode = config['configs']['mode']['runner']
    if mode == 'rs':
        mainRealSense(config['configs'])
    elif mode == 'ids':
        mainIDS(config['configs'])
    elif mode == 'usb':
        mainUSB(config['configs'])
    elif mode == 'offvid':
        mainOfflineVideo(config['configs'])
    else:
        mainOfflineImage(config['configs'])


# Run the main function
if __name__ == '__main__':
    main()
