from configparser import ConfigParser
import os

# Get the configparser object
config = ConfigParser()


def init_config():
    if not os.path.isfile('config.ini'):
        config["Locations"] = {
            "demo_dir": "D:\\Libraries\\Onedrive\\University\\4 - Third Year\\1 - PRBX\\Demos",
            "event_url": "https://www.hltv.org/results?event=4866"
        }

        with open('config.ini', 'w') as file:
            config.write(file)


init_config()
