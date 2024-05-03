from fastapi import FastAPI, HTTPException
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import unquote

import asyncio
from concurrent.futures import ThreadPoolExecutor

import traceback
from requests.exceptions import RequestException

from scraper import Scraper

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=4)

def fetch(url):
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    return str(soup)

@app.get("/crawl/")
async def read_root(url: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, fetch, url)
    return {"html": result}

def naver_task(keywords: str):
    try:
        scraper = Scraper()
        result = scraper.scrape_naver(keywords)
        return result
    except Exception as e:
        traceback.print_exc()
        print(f'naver_task error: {e}')
    finally:
        scraper.driver.quit()

@app.get("/search/naver")
async def search_naver(keywords: str):
    try:
        loop = asyncio.get_event_loop()
        keywords = unquote(keywords, encoding='utf-8')
        result = await loop.run_in_executor(executor, naver_task, keywords)

        return result
    except RequestException:
        asyncio.sleep(3)
        result = await loop.run_in_executor(executor, naver_task, keywords)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
def naver_shopping_task(keywords: str):
    try:
        scraper = Scraper()
        result = scraper.scrape_navershopping(keywords)
        return result
    except Exception as e:
        traceback.print_exc()
        print(f'naver_shopping_task error: {e}')
    finally:
        scraper.driver.quit()

@app.get("/search/navershopping")
async def search_naver_shopping(keywords: str):
    try:
        loop = asyncio.get_event_loop()
        keywords = unquote(keywords, encoding='utf-8')
        result = await loop.run_in_executor(executor, naver_shopping_task, keywords)

        return result
    except RequestException:
        asyncio.sleep(3)
        result = await loop.run_in_executor(executor, naver_shopping_task, keywords)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))