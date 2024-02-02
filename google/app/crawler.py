from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller


import sys
import time
import os

class Crawler():
    def __init__(self) -> None:
        
        self.driver = None
        pass

    def Set_Browser(self):
        chromedriver_autoinstaller.install()
        # chromedriver_path = '../chromedriver'
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('no-sandbox')
        options.add_argument('--disable-extensions')
        options.add_argument('--temp-profile')
        options.add_argument('--disable-features=SearchProviderFirstRun')
        options.add_argument('--disable-geolocation')

        if self.driver == None:
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver.quit()
            self.driver = webdriver.Chrome(options=options)

    def Search_Google(self, keyword:str, delay:float):
        url = f'https://www.google.com/search?q={keyword}'
        self.driver.get(url)
        succesed = False
        wait = WebDriverWait(self.driver, 5)
        try:
            elements = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 's75CSd'))
            )
            # elements = self.driver.find_elements(By.CLASS_NAME, 's75CSd')
            result = []
            for element in elements:
                result.append(element.text)
            succesed = True
                
        except NoSuchElementException:
            result = ['관련검색어가 없습니다.']
            succesed = False

        except TimeoutException:
            print('Timeout')
            result = ['관련검색어가 없습니다.']    
            suceesed = False

        except WebDriverException:
            print("WebDriverException")
            self.Search_Google(keyword=keyword, delay=0)

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