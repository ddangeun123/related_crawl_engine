from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium_driver import SeleniumDriver
import time
import datetime
import traceback
from bs4 import BeautifulSoup
import json

class Scraper:
    def __init__(self):
        # Initialize any necessary variables or objects here
        self.driver = SeleniumDriver().set_up()
        self.retry = 0
        self.scroll_position = 0
        pass

    def scrape_youtube(self, query:str, limit:int = 250):
        driver = self.driver
        driver.get(f'https://www.youtube.com/results?search_query={query}')
        thumbnails = []
        while len(thumbnails) < limit:
            try:
                self.scroll_down(driver)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, 'thumbnail')))
                thumbnails = driver.find_elements(By.ID, 'thumbnail')
            except TimeoutException:
                print('TimeoutException')
        hrefs = [thumbnail.get_attribute('href') for thumbnail in thumbnails]
        print(f'{len(hrefs)} 개 url 수집')
        results = []
        for url in hrefs:
            try:
                result = self.get_video_detail(url)
                print(result)
                results.append(result)
            except Exception as e:
                print(f'Error: {e}')
                traceback.print_exc()
        return results
        pass
    def get_video_detail(self, url:str):
        driver = self.driver
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'above-the-fold')))
        expand_button = driver.find_element(By.ID, 'expand-sizer')
        ActionChains(driver).move_to_element(expand_button).click().perform()
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        description = soup.find(id='description-inline-expander').text
        info_container = soup.find(id='info-contents')
        info_ele = info_container.find(id='info')
        auto_eles = info_ele.find_all(dir='auto')
        # viewCount = auto_eles[0].text.split('조회수 ')[1].split('회')[0]
        # publishDate = self.parse_datetime(auto_eles[2].text)
        videoid = driver.current_url.split('v=')[1]
        title = driver.title.split(' - YouTube')[0]
        author = soup.find(id='upload-info').text
        
        # publishDate = self.parse_datetime(publishDate)
        result = {
                    "VideoID": videoid,
                    "title": title,
                    "description": description,
                    # "viewCount": viewCount,
                    "author": author,
                    # "publishDate": publishDate,
                    # "comments":{
                    #     "count":comments_res['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][1]['text'],
                    #     "comments":comments
                    # }
                }
        return result
    def scroll_down(self, driver:Chrome):
        self.scroll_position += 700
        driver.execute_script(f"window.scrollTo(0, {self.scroll_position})")
    def parse_datetime(self, date_str:str):
        date_str = date_str.replace('.', '').strip()  # '2021 2 28' 변환
        year, month, day = map(int, date_str.split())  # 각 부분을 정수로 변환

        date = datetime.datetime(year, month, day)  # datetime 객체 생성
        return date

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_youtube('검은콩')