from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from configparser import ConfigParser
import logging
import json
import patoolib
import shutil

EVENTS = []
HLTV_BASE_URL = "https://www.hltv.org/"

# Reads config file to find directory of demo files
config = ConfigParser()
config.read("data\\config.ini")

DEMO_DIR = config["Data"]["demo_directory"]

ARCHIVE_DIR = DEMO_DIR + "\\archives"
EXTRACTED_DIR = DEMO_DIR + "\\mirage_demos"

METADATA_DIR = DEMO_DIR + "\\metadata"
DEMO_ID_FILE = METADATA_DIR + "\\saved_match_ids.json"
RESULTS_URL_FILE = METADATA_DIR + "\\results_urls.json"
MATCH_URL_FILE = METADATA_DIR + "\\match_urls.json"

logging.basicConfig(level=logging.INFO, filename='logs//scraper.log',
                    filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def init_driver(download_path=ARCHIVE_DIR, headless=True):
    '''
    Initializes and returns web driver object with logging messages hidden.
    '''
    logging.info("Initializing Chrome Web Driver...")
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option(
        'prefs', {'download.default_directory': download_path})
    return webdriver.Chrome(options=options)


def get_results_page_urls():
    ''' Returns all results page URLs for regional, international & major LANs between 20/02/2020 & 10/4/2022 due
        to dataset constraints'''

    logging.info("Collecting results page URLS... ")
    start_time = time.time()

    if os.path.exists(RESULTS_URL_FILE):
        logging.info(
            f"Event URLs already collected, returning data from file [{RESULTS_URL_FILE}]")
        with open(RESULTS_URL_FILE, 'r') as f:
            return json.load(f)

    else:
        RESULTS_BASE = "https://www.hltv.org/results?event="
        results_urls = []
        driver = init_driver()
        events_list_url = "https://www.hltv.org/events/archive?startDate=2020-02-20&endDate=2022-04-10&eventType=MAJOR&eventType=INTLLAN&eventType=REGIONALLAN"

        # Navigates to filtered page containing all regional, international & major LANs between 20/02/2020 & 10/4/2022
        driver.get(events_list_url)

        # Gets all event containers
        events = driver.find_elements(
            by=By.XPATH, value="//div[@class='events-page']/div/a[@class='a-reset small-event standard-box']")

        for event in events:
            event_page = event.get_attribute("href")
            event_id = event_page.split("/")[-2]

            # For each event found, extracts event ID and adds to results base url
            results_urls.append(RESULTS_BASE + event_id)
            logging.info(
                f"Adding results URL for EVENT_ID - {event_id}")

        driver.close()

        # Saves all result page urls to file
        with open(RESULTS_URL_FILE, 'w') as f:
            json.dump(results_urls, f, indent=2)

        logging.info(
            f"Saving all results page URLs to file [{RESULTS_URL_FILE}]")
        logging.info(f"Number of events found - {len(results_urls)}")
        logging.info(
            f"Time taken to execute - {time.time() - start_time:.2f}s")
        return results_urls


def get_match_urls(results_pages):
    '''
    Returns the all HLTV match URLs found on an events results page if the match involved mirage.
    '''
    logging.info("Collecting match page URLS... ")
    start_time = time.time()

    if os.path.exists(MATCH_URL_FILE):
        logging.info(
            f"Match URLs already collected returning data from file [{MATCH_URL_FILE}]")
        with open(MATCH_URL_FILE, 'r') as f:
            return json.load(f)
    else:
        driver = init_driver()
        match_urls = {}

        for results_page in results_pages:
            event_id = results_page.split("=")[-1]
            logging.info(
                f"Finding all match result URLS for EVENT_ID - {event_id}")
            # Navigates to the results page
            driver.get(results_page)

            # Saves each match url from the results page
            results = driver.find_elements(
                by=By.XPATH, value="//div[@class='result-con']/a")
            for match in results:
                match_url = match.get_attribute("href")
                match_id = match_url.split("/")[-2]
                logging.info(f"Adding URL for MATCH_ID - {match_id}")
                match_urls[match_id] = match_url

            # Checks the list of maps played on each url and deletes it from the dictionary if de_mirage wasn't played.
            matches_to_delete = []
            for match_id, url in match_urls.items():
                driver.get(url)
                played_maps = [elm.text for elm in driver.find_elements(
                    by=By.XPATH, value="//div[@class='played']/div/div[@class='mapname']")]

                if "Mirage" not in played_maps:
                    matches_to_delete.append(match_id)
                    logging.info(
                        f"Deleting URL for MATCH_ID - {match_id} as de_mirage was not played")

            for id in matches_to_delete:
                del match_urls[id]

        driver.quit()

        # Saves all match urls to file
        with open(MATCH_URL_FILE, 'w') as f:
            json.dump(match_urls, f, indent=2)

        logging.info(
            f"Saving all match URLs to file [{MATCH_URL_FILE}]")

        logging.info(f"Number of matches found - {len(match_urls.keys())}")
        logging.info(
            f"Time taken to execute - {time.time() - start_time:.2f}s")
        return match_urls


def download_demos(match_urls):
    '''
    Downloads a demo file from a match page into the demo directory inside a folder named after the event.
    Prevents duplicate download if demo id is already stored in the demo id file.
    '''
    # Checks if a folder for the event already exists, otherwise creates one
    driver = init_driver(headless=True)

    downloaded_demo_ids = []
    if os.path.exists(DEMO_ID_FILE):
        logging.info(f"Demo ID file exists at [{DEMO_ID_FILE}], loading ")
        with open(DEMO_ID_FILE, 'r') as f:
            downloaded_demo_ids = json.load(f)

    for demo_id, url in match_urls.items():
        if demo_id not in downloaded_demo_ids:
            driver.get(url)

            # Finds the download demo button and extracts demo ID from URL
            demo_button = driver.find_element_by_xpath(
                "//*[text() = 'GOTV Demo']")
            demo_button.click()

            logging.info(f"Downloading DEMO_ID - {demo_id}")
            download_wait(DEMO_DIR)
            downloaded_demo_ids.append(demo_id)
            with open(DEMO_ID_FILE, 'w') as f:
                json.dump(downloaded_demo_ids, f, indent=2)
        else:
            logging.info(
                f"DEMO_ID {demo_id} already downloaded - Skipping...")
    logging.info("All match demos successfully downloaded")


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


def extract_demos():
    logging.info("Extracting .rar files...")
    if len(os.listdir(EXTRACTED_DIR)) != 0:
        logging.info(
            "Previously Extracted demos found. Please clear directory or continue.")
    else:
        for file in os.listdir(ARCHIVE_DIR):
            if file.endswith(".rar"):
                temp_dir = ARCHIVE_DIR + "\\" + file.split(".")[0]
                os.mkdir(temp_dir)
                patoolib.extract_archive(
                    ARCHIVE_DIR + "\\" + file, outdir=temp_dir, verbosity=-1)
                for file in os.listdir(temp_dir):
                    file_name = file.replace(".dem", "")
                    map_played = file_name.split("-")[-1]
                    archive_name = temp_dir.split("\\")[-1]
                    new_file_name = archive_name + "-" + map_played + ".dem"
                    os.rename(temp_dir + "\\" + file,
                              temp_dir + "\\" + new_file_name)

                    if map_played.lower() == "mirage":
                        os.replace(temp_dir + "\\" + new_file_name,
                                   EXTRACTED_DIR + "\\" + new_file_name)
                shutil.rmtree(temp_dir)

                logging.info(f"Extraction of {file} Complete")
        logging.info(f"Demo file extraction complete")


# results_urls = get_results_page_urls()
# match_urls = get_match_urls(results_urls)
# download_demos(match_urls)
# extract_demos()
