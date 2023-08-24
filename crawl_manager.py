from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import sys
import time


class Crawler():
    def __init__(self) -> None:
        self.driver = None
        pass

    def Set_Browser(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('no-sandbox')
        options.add_argument('--disable-extensions')

        if self.driver == None:
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver.quit()
            self.driver = webdriver.Chrome(options=options)
            
    def Search_Naver(self, keyword:str, delay:float):
        result = []
        url = f'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={keyword}'
        self.driver.get(url=url)
        try:
            target = self.driver.find_element(By.CLASS_NAME, 'lst_related_srch')
            elements = target.find_elements(By.CLASS_NAME, 'tit')
            for ele in elements:
                result.append(ele.text)

            data ={
                'keyword':keyword,
                'result':result,
                'popular_contents':''
            }
        except Exception as e:
            result = '관련검색어가 없습니다.'
            data = {
                'keyword':keyword,
                'result':result,
                'popular_contents':''
            }

        try:
            popular_element = self.driver.find_element(By.CLASS_NAME, 'intent_popular_wrap')
            elements = popular_element.find_elements(By.CLASS_NAME, 'dsc')
            popular_contents = []
            for ele in elements:
                popular_contents.append(ele.text)
            
            data = {
                'keyword':keyword,
                'result':result,
                'popular_contents':popular_contents
            }
        except Exception as e:
            popular_contents = '인기 주제가 없습니다.'
            data = {
                'keyword':keyword,
                'result':result,
                'popular_contents':popular_contents
            }

        return data, True
    def Search_Google(self, keyword:str, delay:float):
        url = f'https://www.google.com/search?q={keyword}'
        self.driver.get(url)
        succesed = False
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, 's75CSd')
            result = []
            for element in elements:
                result.append(element.text)
            succesed = True
                
        except NoSuchElementException:
            result = ['관련검색어가 없습니다.']
            succesed = False

        except Exception as e:
            print(f'예상치 못한 오류가 발생했습니다. 오류코드 : {sys.exc_info.__name__}')
            result = ['관련검색어가 없습니다.']
            succesed = False
        
        finally:
            json_result = {
                'keyword':keyword,
                'result':result
            }
            return json_result, succesed
        
    def Search_NaverShopping(self, keyword, delay:float):
        result = []
        url = f'https://msearch.shopping.naver.com/search/all?query={keyword}&prevQuery={keyword}'
        self.driver.get(url=url)
        try:
            time.sleep(delay)
            target = self.driver.find_element(By.CLASS_NAME, 'intentKeyword_pannel_inner__e93lz')
            elements = target.find_elements(By.TAG_NAME, 'a')
            for ele in elements:
                result.append(ele.text)

            data ={
                'keyword':keyword,
                'result':result,
            }
        except Exception as e:
            result = '관련검색어가 없습니다.'
            data = {
                'keyword':keyword,
                'result':result,
            }

        return data, True
    
