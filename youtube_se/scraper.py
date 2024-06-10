from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium_driver import SeleniumDriver
import pytz
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

    def scrape_youtube(self, query:str, limit:int = 100):
        driver = self.driver
        driver.get(f'https://www.youtube.com/results?search_query={query}')
        thumbnails = []
        urls = []
        while len(urls) < (limit * 1.3):
            try:
                self.scroll_down(driver)
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_all_elements_located((By.ID, 'thumbnail')))
                thumbnails = driver.find_elements(By.ID, 'thumbnail')
                hrefs = [thumbnail.get_attribute('href') for thumbnail in thumbnails]
                urls = [url for url in hrefs if url is not None and ('shorts' in url or 'watch' in url)]
                urls = set(urls)
            except TimeoutException:
                print('TimeoutException')
        
        print(f'{len(urls)} 개 url 수집')
        results = []
        for url in hrefs:
            if limit <= 0:
                break
            if url == None:
                continue
            if 'shorts' in url:
                try:
                    result = self.get_shorts_detail(url)
                    results.append(result)
                    limit -= 1
                except TimeoutException:
                    print(url, 'TimeoutException')
                    self.driver.refresh()
                    try:
                        result = self.get_shorts_detail(url)
                        limit -= 1
                    except:
                        result = {
                            "VideoID"        : url.split('shorts/')[1],
                            "title"          : '',
                            "type"           : "shorts",
                            "description"    : '',
                            "viewCount"      : '',
                            "author"         : '',
                            "publishDate"    : '',
                            "Error"          : 'TimeoutException'
                        }
                        results.append(result)
                        limit -= 1
                        pass
                    continue
                except Exception as e:
                    print(f'Error: {e}')
                    traceback.print_exc()
                    continue
            elif 'watch' in url:
                try:
                    result = self.get_video_detail(url)
                    results.append(result)
                    limit -= 1
                except TimeoutException:
                    print(url, 'TimeoutException')
                    self.driver.refresh()
                    try:
                        result = self.get_video_detail(url)
                        limit -= 1
                    except:
                        result = {
                            "VideoID"        : url.split('v=')[1],
                            "title"          : '',
                            "type"           : "video",
                            "description"    : '',
                            "viewCount"      : '',
                            "author"         : '',
                            "publishDate"    : '',
                            "Error"          : 'TimeoutException'
                        }
                        results.append(result)
                        limit -= 1
                        pass
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
        for _ in range(3):
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, 'microformat')))
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            micro_format = soup.select_one('#microformat')
            
            if micro_format is not None:
                break

        script_ele = micro_format.find('script', {'type':'application/ld+json'})
        json_text = script_ele.text
        json_data = json.loads(json_text)
        description = json_data.get("description", "No description found")
        view_count = json_data.get("interactionCount", "No view count found")
        title = json_data.get("name", "No title found")
        publish_date = json_data.get("uploadDate", "No publish date found")
        author = json_data.get("author", "No author found")

        videoid = driver.current_url.split('v=')[1]
        
        result = {
                    "VideoID"        : videoid,
                    "type"           : "video",
                    "title"          : title,
                    "description"    : description,
                    "viewCount"      : view_count,
                    "author"         : author,
                    "publishDate"    : publish_date,
                    "Error"          : "None"
                    # "comments":{
                    #     "count":comments_res['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][1]['text'],
                    #     "comments":comments
                    # }
                }
        print(result)
        return result
    
    def get_shorts_detail(self, url:str):
        # 변수 초기화
        videoid = ''
        title = ''
        description = ''
        view_count = 0
        author = ''
        publish_date = ''
        driver = self.driver
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'menu-button')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        videoid = driver.current_url.split('shorts/')[1]
        try:
            panel = soup.find(class_='short-video-container')
            items = panel.find(id='items')
            title = items.find(id='title').text
            try:
                description = items.find(id='description').text
            except:
                description = ''
            try:
                factoid_value = items.find('view-count-factoid-renderer').find(class_='YtwFactoidRendererValue').text
                view_count = int(factoid_value.replace(',', ''))
            except:
                view_count = 0
            try:
                factoids = items.find(id='factoids').find_all('factoid-renderer')
                for factoid in factoids:
                    text = factoid.text
                    if '년' in text and '월' in text and '일' in text:
                        date_text = text
                        break
                # Extract the numbers
                numbers = re.findall(r'\d+', date_text)

                # Extract the year, month, and day and their positions
                elements = [('년', text.index('년')), ('월', text.index('월')), ('일', text.index('일'))]

                # Sort the elements based on their positions
                elements.sort(key=lambda x: x[1])

                # Map the elements to the numbers
                date_elements = {elements[i][0]: int(numbers[i]) for i in range(3)}

                # Create a datetime object
                publish_date = datetime.datetime(date_elements['년'], date_elements['월'], date_elements['일']).isoformat()

                print(publish_date)
            except Exception as e:
                traceback.print_exc()
                publish_date = -1
            author = soup.find(id='channel-name').find(id='text-container').text

            # video_obj = soup.find(id='watch7-content')
            # videoid = video_obj.find('meta', {'itemprop':'identifier'})['content']
            # title = video_obj.find('meta', {'itemprop':'name'})['content']
            # description = video_obj.find('meta', {'itemprop':'description'})['content']
            # author = video_obj.find('span', {'itemprop':'author'}).find('link', {'itemprop':'name'})['content']
            # view_count = video_obj.find('meta', {'itemprop':'interactionCount'})['content']
            # publish_date = video_obj.find('meta', {'itemprop':'uploadDate'})['content']

            result = {
                        "VideoID"        : videoid,
                        "title"          : title,
                        "type"           : "shorts",
                        "description"    : description,
                        "viewCount"      : view_count,
                        "author"         : author,
                        "publishDate"    : publish_date,
                        "Error"          : "None"
                        # "comments":{
                        #     "count":comments_res['onResponseReceivedEndpoints'][0]['reloadContinuationItemsCommand']['continuationItems'][0]['commentsHeaderRenderer']['countText']['runs'][1]['text'],
                        #     "comments":comments
                        # }
                    }
            print(result)
            return result
        except Exception as e:
            result = {
                        "VideoID"        : videoid,
                        "title"          : title,
                        "type"           : "shorts",
                        "description"    : description,
                        "viewCount"      : view_count,
                        "author"         : author,
                        "publishDate"    : publish_date,
                        "Error"          : e
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
        try:
            date_str = date_str.replace('.', '').strip()  # '2021 2 28' 변환
            year, month, day = map(int, date_str.split())  # 각 부분을 정수로 변환

            date = f"{year}-{month:02d}-{day:02d}"  # 문자열 포맷팅을 사용하여 날짜 생성
            return date
        except:
            return "0000-00-00"
    def convert_korean_date_to_iso(self, date_string):
        # 특수문자와 공백, 개행 문자 제거
        clean_string = re.sub(r'[\s\n\t\r]+', ' ', date_string)  # 공백으로 변환
        clean_string = re.sub(r'[^0-9년월일\s]', '', clean_string)  # 숫자와 년월일, 공백 제외하고 제거

        # 다양한 날짜 패턴
        patterns = [
            re.compile(r'(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일'),  # YYYY년 MM월 DD일
            re.compile(r'(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*(\d{4})\s*년'),  # MM월 DD일 YYYY년
            re.compile(r'(\d{1,2})\s*일\s*(\d{1,2})\s*월\s*(\d{4})\s*년'),  # DD일 MM월 YYYY년
            re.compile(r'(\d{4})\s*년\s*(\d{1,2})\s*일\s*(\d{1,2})\s*월'),  # YYYY년 DD일 MM월
            re.compile(r'(\d{1,2})\s*월\s*(\d{4})\s*년\s*(\d{1,2})\s*일'),  # MM월 YYYY년 DD일
            re.compile(r'(\d{1,2})\s*일\s*(\d{4})\s*년\s*(\d{1,2})\s*월')   # DD일 YYYY년 MM월
        ]

        for pattern in patterns:
            match = pattern.search(clean_string)
            if match:
                parts = match.groups()
                if '년' in clean_string and '월' in clean_string and '일' in clean_string:
                    year, month, day = parts[0], parts[1], parts[2]
                    if '월' in clean_string.split('년')[1]:  # YYYY년 MM월 DD일
                        return f"{year}-{month}-{day}"
                    elif '일' in clean_string.split('월')[1]:  # MM월 DD일 YYYY년
                        return f"{parts[2]}-{parts[0]}-{parts[1]}"
                    elif '년' in clean_string.split('월')[1]:  # MM월 YYYY년 DD일
                        return f"{parts[1]}-{parts[0]}-{parts[2]}"
                    elif '월' in clean_string.split('일')[1]:  # DD일 MM월 YYYY년
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elif '일' in clean_string.split('년')[1]:  # YYYY년 DD일 MM월
                        return f"{parts[0]}-{parts[2]}-{parts[1]}"
                    elif '년' in clean_string.split('일')[1]:  # DD일 YYYY년 MM월
                        return f"{parts[1]}-{parts[2]}-{parts[0]}"
                break
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
    result = scraper.scrape_youtube('검은콩', limit=10)
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/EM82-sveZCc'))
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/9sCO-7mJZzM'))
    # 비디오 에러
    # 비디오 더보기 안눌러짐 (headless모드)  해결
    # scraper.get_video_detail('https://www.youtube.com/watch?v=1y4wwT69c80')

    # Timeout 시 새로고침 해보기
    
    # 쇼츠 에러 다른 버튼 클릭 url
    # print(scraper.get_shorts_detail('https://www.youtube.com/shorts/F6Sep9-cWaM'))
    # 쇼츠 조회수가 아닌 좋아요 수로 나옴
    # 쇼츠 날짜 표기 다른 형식   해결
    
    
    