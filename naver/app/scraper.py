from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By

from driver_manager import DriverManager
import time
from bs4 import BeautifulSoup


class Scraper:
  def __init__(self, driver, driver_manager:DriverManager):
    # Initialize any necessary variables or objects here
    self.driver = driver
    self.driver_manager = driver_manager
    self.retry = 0
    pass

  def scrape_naver(self, keyword:str, delay:float=0):
    # Implement your scraping logic here
    result = []
    url = f'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={keyword}'
    try:
      self.driver.get(url=url)
      wait = WebDriverWait(self.driver, 10)
      target = self.driver.find_element(By.CLASS_NAME, 'lst_related_srch')
      wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tit')))
      elements = target.find_elements(By.CLASS_NAME, 'tit')
      for ele in elements:
        if ele.text != '':
          result.append(ele.text)
    except NoSuchElementException:
      result = '관련검색어가 없습니다.'
    except TimeoutException:
      self.driver.refresh()
      self.retry += 1
      if self.retry < 2:
        return self.scrape_naver(keyword=keyword, delay=delay)
      else:
        result = '관련검색어가 없습니다.'

        # 종료 함수 수정
        self.driver = self.driver_manager.restart_driver(self.driver)
        self.retry = 0
    except WebDriverException:
      self.retry += 1
      if self.retry < 2:
        return self.scrape_naver(keyword=keyword, delay=delay)
      else:
        result = '관련검색어가 없습니다.'

        # 종료 함수 수정
        self.driver = self.driver_manager.restart_driver(self.driver)
        self.retry = 0
    data = {
        'keyword': keyword,
        'result': result,
    }
    print(data)
    return data, True

  def scrape_navershopping(self, keyword:str, delay:float=0):
    url = f'https://msearch.shopping.naver.com/search/all?query={keyword}&prevQuery={keyword}'
    self.driver.get(url=url)
    time.sleep(delay)
    wait = WebDriverWait(self.driver, 10)

    try:
      wait.until(EC.presence_of_all_elements_located((By.ID, 'taglist')))
      page_source = self.driver.page_source
      soup = BeautifulSoup(page_source, 'html.parser')
      targets = soup.select('.intentKeyword_list_panel__thfp_ a')
      result = [tag.text for target in targets for tag in target.find_all('a')]

      if len(result) <= 0:
        temp_ul = soup.select_one('#taglist div ul')
        li_tags = temp_ul.find_all('li')
        result = [li.text for li in li_tags]

      data = {
        'keyword': keyword,
        'result': result,
      }
    except TimeoutException:
      self.retry += 1
      if self.retry < 2:
        return self.scrape_navershopping(keyword=keyword, delay=delay)
      else:
        result = '관련검색어가 없습니다.'
        data = {
            'keyword': keyword,
            'result': result,
        }

        # 종료 함수 수정
        self.driver = self.driver_manager.restart_driver(self.driver)
        self.retry = 0
    except WebDriverException:
      self.retry += 1
      if self.retry < 2:
          return self.scrape_navershopping(keyword=keyword, delay=delay)
      else:
        result = '관련검색어가 없습니다.'
        data = {
            'keyword': keyword,
            'result': result,
        }
        self.driver = self.driver_manager.restart_driver(self.driver)
        self.retry = 0

    except Exception as e:
      print(e)
      data = {
          'keyword': keyword,
          'result': '관련 검색어가 없습니다.',
      }
      self.driver = self.driver_manager.restart_driver(self.driver)
    print(data)
    return data, True

if __name__ == '__main__':
  # Example usage:
  driver_manager = DriverManager()
  scraper = Scraper(driver=driver_manager.get_available_driver(), driver_manager=driver_manager)
  scraper.scrape_naver(keyword='제일기획', delay=0.5)
  scraper.scrape_navershopping(keyword='제일기획', delay=0.5)
  scraper.scrape_navershopping(keyword='초콜릿', delay=0.5)
