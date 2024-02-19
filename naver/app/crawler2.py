from selenium.webdriver import Chrome, ChromeOptions


class Scraper():
    def __init__(self):
        self.options = ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.driver = Chrome(options=self.options)

    def get(self, url):
        self.driver.get(url)
        return self.driver.page_source

    def __del__(self):
        self.driver.close()

    def select_element_by_classname(self, name):
        return self.driver.find_element_by_class_name(name)
        