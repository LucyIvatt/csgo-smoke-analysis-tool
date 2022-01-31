from selenium import webdriver
import os
import time
from constants import DEMO_DIR


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
    dl_path = DEMO_DIR + "\\" + event_name
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


# name, results = get_match_urls(HLTV_URL)
# write_links_to_file("test", name, results)
download_demo("BLAST Premier Spring Groups 2022",
              "https://www.hltv.org/matches/2353976/mibr-vs-astralis-blast-premier-spring-groups-2022")
