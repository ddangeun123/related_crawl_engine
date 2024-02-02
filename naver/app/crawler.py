from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import chromedriver_autoinstaller

from bs4 import BeautifulSoup


import sys
import time
import os

class Crawler():
    def __init__(self) -> None:
        
        self.driver = None
        pass

    def Set_Browser(self):
        chromedriver_autoinstaller.install()
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

        if self.driver == None:
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver.quit()
            self.driver = webdriver.Chrome(options=options)

    def Search_Naver(self, keyword:str, delay:float):
        result = []
        url = f'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={keyword}'
        self.driver.get(url=url)
        wait = WebDriverWait(self.driver, 10)
        try:
            target = self.driver.find_element(By.CLASS_NAME, 'lst_related_srch')
            wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'tit'))
            )
            elements = target.find_elements(By.CLASS_NAME, 'tit')
            for ele in elements:
                result.append(ele.text)

            data ={
                'keyword':keyword,
                'result':result,
            }
        except WebDriverException as e:
            self.Search_Naver(keyword=keyword, delay=delay)
        except Exception as e:
            result = '관련검색어가 없습니다.'
            data = {
                'keyword':keyword,
                'result':result,
            }
        return data, True
    
    def Search_NaverShopping(self, keyword, delay:float):
        result = []
        url = f'https://msearch.shopping.naver.com/search/all?query={keyword}&prevQuery={keyword}'
        self.driver.get(url=url)
        time.sleep(delay)
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            targets = soup.find_all(class_='intentKeyword_list_pannel__thfp_')
            result = []
            for target in targets:
                a_tags = target.find_all('a')
                for tag in a_tags:
                    result.append(tag.text)

            data ={
                'keyword':keyword,
                'result':result,
            }
        except WebDriverException as e:
            self.Search_NaverShopping(keyword=keyword, delay=delay)
        except Exception as e:
            print(e)
            data ={
                'keyword':keyword,
                'result':"관련 검색어가 없습니다.",
            }
        

        return data, True