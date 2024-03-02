from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By

from driver_manager import DriverManager
import sys
import time

class Scraper:
  def __init__(self, driver, driver_manager:DriverManager):
    # Initialize any necessary variables or objects here
    self.driver = driver
    self.driver_manager = driver_manager
    self.retry = 0
    pass

  def scrape_google(self, keyword:str, delay:float=0):
    # Implement your scraping logic here
    url = f'https://www.google.com/search?q={keyword}'
    self.driver.get(url)
    succesed = False
    wait = WebDriverWait(self.driver, 10)
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
        print(f'{keyword} Timeout')
        
        if self.retry < 2:
          self.driver.refresh()
          self.retry += 1
          return self.scrape_google(keyword=keyword, delay=delay)
        else:
          result = ['관련검색어가 없습니다.']

          self.retry()
          time.sleep(5)

    except WebDriverException:
        print("WebDriverException")
        if self.retry < 2:
            return self.scrape_google(keyword=keyword, delay=delay)
        else:
            result = ['관련검색어가 없습니다.']
            self.retry()

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
    
  def retry(self):
      self.driver = self.driver_manager.restart_driver(self.driver)
      self.retry = 0