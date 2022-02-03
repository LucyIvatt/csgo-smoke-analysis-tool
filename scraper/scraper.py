from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from configparser import ConfigParser

HLTV_BASE_URL = "https://www.hltv.org/"

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Locations"]["demo_dir"]


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)


def find_event_results_url(event_name):
    driver = init_driver()
    driver.get(HLTV_BASE_URL)

    burger = driver.find_element_by_xpath(
        "//div[@class='navburger navburger2']")
    burger.click()
    search_bar = driver.find_element_by_css_selector(
        "input[placeholder='Search...']")
    search_bar.send_keys(event_name)
    time.sleep(2)
    event_link = driver.find_element_by_xpath(
        "//div[@class='box eventsearch expanded hoverable']/div/a")
    driver.get(event_link.get_attribute("href"))

    results_page = driver.find_element_by_xpath(
        "//div[@class='event-hub-bottom']/a[contains(text(), 'Results')]")
    return results_page.get_attribute("href")


def get_match_urls(event_url):
    driver = webdriver.Chrome()
    driver.get(event_url)

    event_name = driver.find_element_by_xpath(
        "//div[contains(@class, 'event-hub-title')]").text()

    results = driver.find_elements_by_xpath("//div[@class='result-con ']/a")

    results_list = []
    for p in range(len(results)):
        results_list.append(results[p].get_attribute("href"))

    driver.quit()
    return (event_name, results_list)


def write_links_to_file(filename, event_name, result_links):
    file = open(filename + ".txt", "w")
    file.write(event_name.upper() + ":" + "\n\n")

    for link in result_links:
        file.write(link + "\n")

    file.close()


def download_demo(event_name, result_page):
    dl_path = demo_dir + "\\" + event_name
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)

    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': dl_path}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get(result_page)
    demo_button = driver.find_element_by_xpath("//*[text() = 'GOTV Demo']")
    demo_button.click()
    download_wait(dl_path)


def download_wait(path_to_downloads):
    dl_wait = True
    while dl_wait:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            print(fname)
            if fname.endswith('.crdownload'):
                dl_wait = True


def download_event_demos(event_url):
    event_name, match_urls = get_match_urls(event_url)
    for match in match_urls:
        download_demo(event_name, match)


print(find_event_results_url("Blast Premier Spring Groups 2022"))
