from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
import chromedriver_autoinstaller

from stem import Signal
from stem.control import Controller

from bs4 import BeautifulSoup

import sys
import time
import os

class Crawler():
    def __init__(self) -> None:
        
        self.driver = None
        pass

    def Set_Browser(self):
        # Chrome Browser Options
        chromedriver_autoinstaller.install()
        # proxy = Proxy()
        # proxy.proxy_type = ProxyType.MANUAL
        # self.tor_socks_proxy = "127.0.0.1"
        # self.tor_socks_port = 9150
        # tor_http_proxy = f"socks5://{self.tor_socks_proxy}:{self.tor_socks_port}"
        # proxy.http_proxy = tor_http_proxy
        # proxy.ssl_proxy = tor_http_proxy

        options = Options()
        # options.add_argument('--proxy-server=%s' % proxy.socks_proxy)
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
            self.retry = 0
        else:
            self.driver.quit()
            self.driver = webdriver.Chrome(options=options)
            self.retry = 0


    def Search_Naver(self, keyword:str, delay:float):
        # self.change_tor_ip()
        result = []
        data = {
                    'keyword':keyword,
                    'result':result,
                }
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
                if ele.text == '':
                    continue
                result.append(ele.text)

            data ={
                'keyword':keyword,
                'result':result,
            }
            return data, True
        except WebDriverException as e:
            self.retry += 1
            if self.retry < 5:
                result, success = self.Search_Naver(keyword=keyword, delay=delay)
                return result, success
            else:
                result = '관련검색어가 없습니다.'
                data = {
                    'keyword':keyword,
                    'result':result,
                }
                self.driver.quit()
                return data, True
        except Exception as e:
            result = '관련검색어가 없습니다.'
            data = {
                'keyword':keyword,
                'result':result,
            }
        # current_ip = self.Get_Current_IP()
        # print(current_ip)
            return data, True
    
    def Search_NaverShopping(self, keyword, delay:float):
        # self.change_tor_ip()
        # result = []
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

            if len(result) <= 0:
                temp_ul = soup.find('div', id='taglist').find('div').find('ul')
                li_tags = temp_ul.find_all('li')
                for li in li_tags:
                    result.append(li.text)

            data ={
                'keyword':keyword,
                'result':result,
            }
        except WebDriverException as e:
            self.retry += 1
            if self.retry < 5:
                result, success = self.Search_NaverShopping(keyword=keyword, delay=delay)
                return result, success
            else:
                result = '관련검색어가 없습니다.'
                data = {
                    'keyword':keyword,
                    'result':result,
                }
                self.driver.quit()
                return data, True
        except Exception as e:
            print(e)
            data ={
                'keyword':keyword,
                'result':"관련 검색어가 없습니다.",
            }
        
        
        return data, True
    
    def Get_Current_IP(self):
        url = f'https://search.naver.com/search.naver?where=nexearch&sm=top_sug.pre&fbm=0&acr=1&acq=%EB%82%B4+ip&qdt=0&ie=utf8&query=%EB%82%B4+ip+%EC%A3%BC%EC%86%8C+%ED%99%95%EC%9D%B8'
        self.driver.get(url=url)
        time.sleep(2)
        try:
            current_ip = self.driver.find_element(By.CLASS_NAME, 'ip_chk_box').text
            return current_ip
        except:
            return "IP주소를 찾을 수 없음"
        
    def change_tor_ip(self):
        with Controller.from_port(port=9151) as controller:
            controller.authenticate(password="3592")
            controller.signal(Signal.NEWNYM)