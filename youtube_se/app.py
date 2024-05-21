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

def youtube_task(keywords: str):
    try:
        scraper = Scraper()
        result = scraper.scrape_youtube(keywords)
        return result
    except Exception as e:
        traceback.print_exc()
        print(f'youtube_task error: {e}')
    finally:
        scraper.driver.quit()

@app.get("/search/youtube")
async def search_youtube(keyword: str):
    try:
        loop = asyncio.get_event_loop()
        keyword = unquote(keyword, encoding='utf-8')
        result = await loop.run_in_executor(executor, youtube_task, keyword)

        return result
    except RequestException:
        asyncio.sleep(3)
        result = await loop.run_in_executor(executor, youtube_task, keyword)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    