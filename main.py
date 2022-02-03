from configparser import ConfigParser
import os

from scraper.scraper import download_demo, find_event_results_page_url, get_match_urls

# Get the configparser object
config = ConfigParser()


def init_config():
    if not os.path.isfile('config.ini'):
        config["Data Set"] = {
            "demo_directory": "D:\\Libraries\\Onedrive\\University\\4 - Third Year\\1 - PRBX\\Demos",
            "event_name": "PGL Major Stockholm 2021"
        }

        with open('config.ini', 'w') as file:
            config.write(file)
    config.read('config.ini')


def init_dataset():
    event_name = config["Data Set"]["event_name"]

    event_results_page_url = find_event_results_page_url(event_name)

    match_urls = get_match_urls(event_results_page_url)
    # for match in match_urls:
    #     download_demo(event_name, match)


init_config()
init_dataset()
