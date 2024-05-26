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
import re

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
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_all_elements_located((By.ID, 'thumbnail')))
                thumbnails = driver.find_elements(By.ID, 'thumbnail')
            except TimeoutException:
                print('TimeoutException')
        hrefs = [thumbnail.get_attribute('href') for thumbnail in thumbnails]
        print(f'{len(hrefs)} 개 url 수집')
        results = []
        for url in hrefs:
            if url == None:
                continue
            if 'shorts' in url:
                try:
                    result = self.get_shorts_detail(url)
                    results.append(result)
                except TimeoutException:
                    print('TimeoutException')
                    continue
                except Exception as e:
                    print(f'Error: {e}')
                    traceback.print_exc()
                    continue
            elif 'watch' in url:
                try:
                    result = self.get_video_detail(url)
                    results.append(result)
                except TimeoutException:
                    print('TimeoutException')
                    continue
                except Exception as e:
                    print(f'Error: {e}')
                    traceback.print_exc()
                    continue
            else:
                pass
        return results
    
    def get_video_detail(self, url:str):
        driver = self.driver
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'above-the-fold')))
        try:
            expand_button = driver.find_element(By.ID, 'expand-sizer')
            ActionChains(driver).move_to_element(expand_button).click().perform()
        except:
            traceback.print_exc()
        
        wait.until(EC.presence_of_element_located((By.ID, 'description-inline-expander')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        description = soup.find(id='description-inline-expander').text
        info_container = soup.find(id='info-contents')
        info_ele = info_container.find(id='info')
        view_count = info_ele.find(class_='view-count').text.split('조회수 ')[1].split('회')[0]
        publish_date = self.parse_datetime(info_ele.find(id='info-strings').text)
        
        videoid = driver.current_url.split('v=')[1]
        title = driver.title.split(' - YouTube')[0]
        author = soup.find(id='upload-info').text
        
        result = {
                    "VideoID"        : videoid,
                    "title"          : title,
                    "description"    : description,
                    "viewCount"      : view_count,
                    "author"         : author,
                    "publishDate"    : publish_date,
                    # "comments":{
                    #     "count":comments_res['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][1]['text'],
                    #     "comments":comments
                    # }
                }
        print(result)
        return result
    
    def get_shorts_detail(self, url:str):
        description = ''
        driver = self.driver
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'menu-button')))

        menu_button = driver.find_element(By.ID, 'menu-button')
        ActionChains(driver).move_to_element(menu_button).click().perform()
        content_wrapper = driver.find_element(By.ID, 'contentWrapper')

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="items"]/ytd-menu-service-item-renderer')))
        info_button = content_wrapper.find_element(By.XPATH, '//*[@id="items"]/ytd-menu-service-item-renderer')
        ActionChains(driver).move_to_element(info_button).click().perform()

        wait.until(EC.presence_of_element_located((By.ID, 'watch-while-engagement-panel')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        soup.find(id='watch-while-engagement-panel')

        try:
            more_button = soup.find(id='more-button')
            ActionChains(driver).move_to_element(more_button).click().perform()
        except:
            pass

        info = driver.find_element(By.ID, 'factoids')
        videoid = driver.current_url.split('shorts/')[1]
        view_count = info.find_element(By.CLASS_NAME, 'YtwFactoidRendererValue').text
        publish_date = self.parse_shorts_datetime(info.find_elements(By.CLASS_NAME, 'YtwFactoidRendererHost')[2].text)
        descript_window = driver.find_elements(By.TAG_NAME, 'ytd-engagement-panel-section-list-renderer')[1]
        try:
            description = descript_window.find_element(By.ID, 'description').text
        except:
            pass
        exit_button = descript_window.find_element(By.ID, 'visibility-button')
        ActionChains(driver).move_to_element(exit_button).click().perform()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'metadata-container')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_data = soup.find(class_='metadata-container')
        author = meta_data.find(id='channel-name').text
        title = meta_data.find(class_='title').text

        result = {
                    "VideoID"        : videoid,
                    "title"          : title,
                    "description"    : description,
                    "viewCount"      : view_count,
                    "author"         : author,
                    "publishDate"    : publish_date,
                    # "comments":{
                    #     "count":comments_res['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][1]['text'],
                    #     "comments":comments
                    # }
                }
        print(result)
        return result

    def scroll_down(self, driver:Chrome):
        self.scroll_position += 700
        driver.execute_script(f"window.scrollTo(0, {self.scroll_position})")
    def parse_datetime(self, date_str:str):
        try:
            date_str = date_str.replace('.', '').strip()  # '2021 2 28' 변환
            year, month, day = map(int, date_str.split())  # 각 부분을 정수로 변환

            date = datetime.datetime(year, month, day)  # datetime 객체 생성
            return date
        except:
            return "0000-00-00"
    def parse_shorts_datetime(self, date_str:str):
        try:
            # 문자열을 개행 문자를 기준으로 분할
            parts = date_str.split('\n')
            
            # 각 부분에서 숫자만 추출
            year = parts[1].replace("년", "").strip()
            month_day = parts[0].split(' ')
            month = month_day[0].replace("월", "").strip()
            day = month_day[1].replace("일", "").strip()
            
            # 결과 문자열 생성
            formatted_date = f"{year}-{int(month)}-{int(day)}"
            return formatted_date
        except:
            return "0000-00-00"

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_youtube('검은콩')
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/EM82-sveZCc'))
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/9sCO-7mJZzM'))
    # 비디오 에러
    # 비디오 더보기 안눌러짐 (headless모드)
    
    # 쇼츠 에러 다른 버튼 클릭 url
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/F6Sep9-cWaM'))
    # 쇼츠 조회수가 아닌 좋아요 수로 나옴
    # 쇼츠 날짜 표기 다른 형식
    
    
    