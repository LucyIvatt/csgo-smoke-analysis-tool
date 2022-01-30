from selenium import webdriver

HLTV_URL = "https://www.hltv.org/results?event=4866"


def get_match_urls(event_url):
    driver = webdriver.Chrome()
    driver.get(event_url)

    event_name = driver.find_elements_by_xpath(
        "//div[contains(@class, 'event-hub-title')]")
    event_name = event_name[0].text

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


name, results = get_match_urls(HLTV_URL)
write_links_to_file("test", name, results)
