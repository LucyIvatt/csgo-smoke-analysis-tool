from selenium import webdriver
import os
import time
from configparser import ConfigParser
import logging

HLTV_BASE_URL = "https://www.hltv.org/"

# Reads config file to find directory of demo files
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Data Set"]["demo_directory"]
demo_id_file = demo_dir + "\\matchids" + ".txt"
logging.basicConfig(level=logging.INFO, filename='scraper.log',
                    filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def init_driver(download_path=demo_dir):
    '''
    Initializes and returns web driver object with logging messages hidden.
    '''
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option(
        'prefs', {'download.default_directory': download_path})
    return webdriver.Chrome(options=options)


def find_event_results_page_url(event_name):
    '''
    Returns the HLTV URL containing the list of match results for a given event.
    '''
    driver = init_driver()
    driver.get(HLTV_BASE_URL)

    # Expands burger menu to show search bar
    burger = driver.find_element_by_xpath(
        "//div[@class='navburger navburger2']")
    burger.click()

    # Searches for the event name & navigates to link provided by search results
    search_bar = driver.find_element_by_css_selector(
        "input[placeholder='Search...']")
    search_bar.send_keys(event_name)
    time.sleep(2)
    event_link = driver.find_element_by_xpath(
        "//div[@class='box eventsearch expanded hoverable']/div/a")
    driver.get(event_link.get_attribute("href"))

    # finds results button on the event page and returns the URL associated with it
    results_page = driver.find_element_by_xpath(
        "//div[@class='event-hub-bottom']/a[contains(text(), 'Results')]")
    results_url = results_page.get_attribute("href")

    driver.quit()
    logging.info('Found event results page url for event ',
                 event_name, " - ", results_url)

    return results_url


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
        match_url = match.get_attribute("href")
        results_list.append(match_url)

        logging.info("Found match page URL for: " + team_one +
                     " Vs " + team_two + " - " + match_url)

    driver.quit()
    logging.info("All matches found for " + event_name)

    return results_list


def write_demo_id_to_file(match_id):
    '''
    Appends a demo id to the demo id file stored in the root of the demo directory.
    '''
    file = open(demo_id_file, "a")
    file.write(match_id + "\n")
    file.close()


def download_demo(event_name, match_page):
    '''
    Downloads a demo file from a match page into the demo directory inside a folder named after the event.

    Prevents duplicate download if demo id is already stored in the demo id file.
    '''
    # Checks if a folder for the event already exists, otherwise creates one
    dl_path = demo_dir + "\\" + event_name
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)

    driver = init_driver(dl_path)
    driver.get(match_page)

    # Finds the download demo button and extracts demo ID from URL
    demo_button = driver.find_element_by_xpath("//*[text() = 'GOTV Demo']")
    demo_link = demo_button.get_attribute("href").split("/")
    demo_id = demo_link[-1]

    with open(demo_id_file) as file:
        # If not a duplicate download, downloads the file and writes ID to demo id file
        if demo_id not in file.read():
            demo_button.click()
            download_wait(dl_path)
            write_demo_id_to_file(demo_id)


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


get_match_urls("ESEA Winter 2021 Cash Cup 3 North America",
               "https://www.hltv.org/results?event=6364")
