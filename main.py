import yaml
from src.runner_rs import runner_rs
from src.runner_ids import runner_ids
from src.runner_usb import runner_usb
from src.runner_offVid import runner_offVid
from src.runner_offImg import runner_offImg


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
        runner_rs(config['configs'])
    elif mode == 'ids':
        runner_ids(config['configs'])
    elif mode == 'usb':
        runner_usb(config['configs'])
    elif mode == 'offvid':
        runner_offVid(config['configs'])
    else:
        runner_offImg(config['configs'])


# Run the main function
if __name__ == '__main__':
    main()
