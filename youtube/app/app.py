from fastapi import FastAPI
from crawler import Crawler
from concurrent.futures import ThreadPoolExecutor
import asyncio

import re
import time

app = FastAPI()
executor = ThreadPoolExecutor(max_workers=4)

def youtube_task(keyword:str, limit:int):
    keyword = keyword.split(',')
    result = []
    crawler = Crawler()
    for index, keyword in enumerate(keyword):
        data = {
            'keyword':keyword,
            'result':crawler.get_info_by_keyword(keyword=keyword, limit=limit, sleep_sec=0.2)
        }
        print(f'{index}   {data}')
        result.append(data)
    if len(result) == 0 :
        for index, keyword in enumerate(keyword):
            data = {
                'keyword':keyword,
                'result':crawler.get_info_by_keyword(keyword=keyword, limit=limit, sleep_sec=0.2)
            }
            print(f'{index}   {data}')
            result.append(data)
    return result

@app.get("/search/youtube")
async def search_youtube(keywords: str, limit:int=250):
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(executor, youtube_task, keywords, limit)
        return result
    except Exception as e:
        print(f'Error: {e}')
        return {'error':str(e)}
    
