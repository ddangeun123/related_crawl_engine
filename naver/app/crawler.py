from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

import time

class Crawler():
    def __init__(self) -> None:
        self.driver = None

    def Set_Browser(self):
        # Chrome Browser Options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--temp-profile')
        options.add_argument('--disable-features=SearchProviderFirstRun')
        options.add_argument('--disable-geolocation')

        if self.driver is None:
            self.driver = webdriver.Chrome(options=options)
            self.retry = 0
        else:
            self.driver.quit()
            self.driver = webdriver.Chrome(options=options)
            self.retry = 0

    def Search_Naver(self, keyword: str, delay: float):
        result = []
        url = f'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={keyword}'
        self.driver.get(url=url)
        wait = WebDriverWait(self.driver, 10)
        try:
            target = self.driver.find_element(By.CLASS_NAME, 'lst_related_srch')
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tit')))
            elements = target.find_elements(By.CLASS_NAME, 'tit')
            for ele in elements:
                if ele.text != '':
                    result.append(ele.text)
        except NoSuchElementException:
            result = '관련검색어가 없습니다.'
        except WebDriverException:
            self.retry += 1
            if self.retry < 5:
                return self.search_naver(keyword=keyword, delay=delay)
            else:
                result = '관련검색어가 없습니다.'
                self.driver.quit()
        data = {
            'keyword': keyword,
            'result': result,
        }
        return data, True

    def Search_NaverShopping(self, keyword, delay: float):
        url = f'https://msearch.shopping.naver.com/search/all?query={keyword}&prevQuery={keyword}'
        self.driver.get(url=url)
        time.sleep(delay)

        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            targets = soup.select('.intentKeyword_list_pannel__thfp_ a')
            result = [tag.text for target in targets for tag in target.find_all('a')]

            if len(result) <= 0:
                temp_ul = soup.select_one('#taglist div ul')
                li_tags = temp_ul.find_all('li')
                result = [li.text for li in li_tags]

            data = {
                'keyword': keyword,
                'result': result,
            }
        except WebDriverException:
            self.retry += 1
            if self.retry < 5:
                return self.search_naver_shopping(keyword=keyword, delay=delay)
            else:
                result = '관련검색어가 없습니다.'
                data = {
                    'keyword': keyword,
                    'result': result,
                }
                self.driver.quit()
                return data, True
        except Exception as e:
            print(e)
            data = {
                'keyword': keyword,
                'result': '관련 검색어가 없습니다.',
            }

        return data, True
        