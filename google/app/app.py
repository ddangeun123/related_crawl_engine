from fastapi import FastAPI, HTTPException
from driver_manager import DriverManager
from scraper import Scraper
import re
from urllib.parse import unquote
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

import traceback
from requests.exceptions import RequestException

app = FastAPI()

executor = ThreadPoolExecutor(max_workers=4)

response_count = 0

def google_task(keywords: str):
    result = {
        'keyword': keywords,
        'result': '검색 결과가 없습니다.'
    }
    try:
        scraper = Scraper()
        # keywords = re.sub(r'[^a-zA-Z0-9 ]', '', keywords)
        result = scraper.scrape_google(keyword=keywords, delay=0.5)
    except Exception as e:
        result = scraper.scrape_google(keyword=keywords, delay=0.5)
    finally:
        return result


@app.get("/search/google")
async def search_google(keywords: str):
    loop = asyncio.get_event_loop()
    try:
        keywords = unquote(keywords, encoding='utf-8')
        result = await loop.run_in_executor(executor, google_task, keywords)
    except RequestException:
        asyncio.sleep(3)
        result = await loop.run_in_executor(executor, google_task, keywords)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        return result
