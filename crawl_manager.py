from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import sys


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
            
    def Search_Naver(self, keyword:str):
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
    def Search_Google(self, keyword:str):
        driver = self.driver
        for _ in range(3):
            driver.execute_script('window.open("https://www.google.com/");')

        tabs = driver.window_handles
        search_count = 0
        total_search_count = 0
        results = []
        for i in range(0, len(keyword)):
            if search_count>=30:
                driver.quit()
                self.driver = webdriver.Chrome(options=self.chrome_option)
                driver = self.driver
                for _ in range(3):
                    driver.execute_script('window.open("https://www.google.com/");')

                tabs = driver.window_handles
                search_count=0

            window_count = len(tabs)
            driver.switch_to.window(tabs[i%window_count])
            driver.get('https://www.google.com/search?q='+keyword[i])
            try:
                elements = driver.find_elements(By.CLASS_NAME, 's75CSd')

                texts = []
                for element in elements:
                    texts.append(element.text)
                json_result = {
                    '검색어' : keyword[i],
                    '관련검색어' : texts
                }
                total_search_count+=1
                search_count+=1


                print(json_result, total_search_count)
                results.append(json_result)
            except NoSuchElementException:
                total_search_count+=1
                search_count+=1

                json_result = {
                '검색어' : keyword[i],
                '관련검색어' : '연관 검색어가 없습니다.'
            }
                print(json_result, total_search_count)
                results.append(json_result)
                # time.sleep(ran)
            except Exception as e:
                return ['알수없는 에러가 발생했습니다. 에러코드 :'+e]

        for i in tabs:
            if i != tabs[0]:
                driver.switch_to.window(i)
                driver.close()
        driver.switch_to.window(tabs[0])
        return results
    def Google_Search_Test(self, keyword):
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
        
    def Search_NaverShopping(self, keyword):
        result = []
        url = f'https://msearch.shopping.naver.com/search/all?query={keyword}&prevQuery={keyword}'
        self.driver.get(url=url)
        try:
            target = self.driver.find_element(By.CLASS_NAME, 'relatedTag_scroll_area__NG5Gs')
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