from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from configparser import ConfigParser
import logging
import json

EVENTS = []
HLTV_BASE_URL = "https://www.hltv.org/"

# Reads config file to find directory of demo files
config = ConfigParser()
config.read("config.ini")
DEMO_DIR = config["Data"]["demo_directory"]
DEMO_ID_FILE = DEMO_DIR + "\\metadata\\match_ids.txt"
RESULT_LINK_FILE = DEMO_DIR + "\\metadata\\results_links.json"
logging.basicConfig(level=logging.INFO, filename='logs//scraper.log',
                    filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def init_driver(download_path=DEMO_DIR):
    '''
    Initializes and returns web driver object with logging messages hidden.
    '''
    logging.info("Initializing Chrome Web Driver...")
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option(
        'prefs', {'download.default_directory': download_path})
    return webdriver.Chrome(options=options)


def get_results_page_urls():
    ''' Returns all results page links for international lans between '''

    if os.path.exists(RESULT_LINK_FILE):
        logging.info("Event link file already exists, returning saved file")
        with open(RESULT_LINK_FILE, 'r') as f:
            results_links = json.load(f)
        return results_links

    else:
        RESULTS_BASE = "https://www.hltv.org/results?event="
        results_links = []
        driver = init_driver()
        link_start = "https://www.hltv.org/events/archive?startDate=2020-02-20&endDate=2022-01-01&eventType=MAJOR&eventType=INTLLAN&eventType=REGIONALLAN"

        # Goes to the page that contains all international LAN events
        driver.get(link_start)

        events = driver.find_elements_by_xpath(
            "//div[@class='events-page']/div/a[@class='a-reset small-event standard-box']")

        for event in events:
            event_page = event.get_attribute("href")
            event_id = event_page.split("/")[-2]
            results_links.append(RESULTS_BASE + event_id)

        with open(RESULT_LINK_FILE, 'w') as f:
            json.dump(results_links, f, indent=2)
        driver.close()
        return results_links


def get_match_urls(event_name, event_results_url):
    '''
    Returns the all HLTV match URLs found on an events results page.
    '''
    driver = init_driver()
    driver.get(event_results_url)

    # appends the link for each result to the list results_list
    results = driver.find_elements_by_xpath("//div[@class='result-con ']/a")
    results_list = []
    logging.info("Finding all match result URLS for " + event_name + "...")
    for match in results:
        team_one = match.find_element_by_xpath(
            ".//div/table/tbody/tr/td/div[@class='line-align team1']/div").text
        team_two = match.find_element_by_xpath(
            ".//div/table/tbody/tr/td/div[@class='line-align team2']/div").text
        vs_string = team_one + " vs " + team_two
        match_url = match.get_attribute("href")
        results_list.append((match_url, vs_string))

        logging.info("Found match page URL for: " +
                     vs_string + " - " + match_url)

    driver.quit()
    logging.info("All matches found for " + event_name +
                 " - Number of matches found: " + str(len(results)))

    return results_list


def write_demo_id_to_file(demo_id):
    '''
    Appends a demo id to the demo id file stored in the root of the demo directory.
    '''
    file = open(DEMO_ID_FILE, "a")
    file.write(demo_id + "\n")
    file.close()
    logging.info("Wrote demo ID: " + demo_id + " to " + DEMO_ID_FILE)


def download_demo(event_name, match_page, vs_string):
    '''
    Downloads a demo file from a match page into the demo directory inside a folder named after the event.

    Prevents duplicate download if demo id is already stored in the demo id file.
    '''
    # Checks if a folder for the event already exists, otherwise creates one
    dl_path = DEMO_DIR + "\\" + event_name
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
        logging.info("Folder for event - " + event_name +
                     " - not found, creating folder...")
    else:
        logging.info("Folder for event - " + event_name +
                     " - found.")

    driver = init_driver(dl_path)
    driver.get(match_page)

    # Finds the download demo button and extracts demo ID from URL
    demo_button = driver.find_element_by_xpath("//*[text() = 'GOTV Demo']")
    demo_link = demo_button.get_attribute("href").split("/")
    demo_id = demo_link[-1]

    with open(DEMO_ID_FILE) as file:
        # If not a duplicate download, downloads the file and writes ID to demo id file
        if demo_id not in file.read():
            demo_button.click()
            logging.info("Downloading demo ID " +
                         demo_id + " - " + vs_string + "...")
            download_wait(dl_path)
            write_demo_id_to_file(demo_id)
        else:
            logging.info("Event ID " + demo_id + "already found in " +
                         DEMO_ID_FILE + ". Skipping...")


def download_wait(path_to_downloads):
    '''
    Waits until the demo download has finished by checking for when the chrome temporary download file is removed from the directory.
    '''
    wait = True
    while wait:
        time.sleep(1)
        wait = False
        for file in os.listdir(path_to_downloads):
            if file.endswith('.crdownload'):
                wait = True
    logging.info("Download finished")


urls = get_results_page_urls()
