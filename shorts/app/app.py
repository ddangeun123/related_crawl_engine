from fastapi import FastAPI
from crawler import Crawler

import re
import time

app = FastAPI()
crawler = Crawler()

@app.get("/search/shorts")
async def search_youtube(keywords: str):
    keywords = keywords.split(',')
    result = []
    for index, keyword in enumerate(keywords):
        data = {
            'keyword':keyword,
            'result':crawler.get_info_by_keyword(keyword=keyword, limit=150, sleep_sec=0.2)
        }
        print(f'{index}   {data}')
        result.append(data)
    if len(result) == 0 :
        for index, keyword in enumerate(keywords):
            data = {
                'keyword':keyword,
                'result':crawler.get_info_by_keyword(keyword=keyword, limit=150, sleep_sec=0.2)
            }
            print(f'{index}   {data}')
            result.append(data)
    return result
@app.get("/search/shorts_test")
async def search_youtube_test(keywords: str):
    keywords = keywords.split(',')
    result = []
    for index, keyword in enumerate(keywords):
        data = {
            'keyword':keyword,
            'result':crawler.get_info_by_keyword(keyword=keyword, limit=5, sleep_sec=0.2)
        }
        print(f'{index}   {data}')
        result.append(data)
    if len(result) == 0 :
        for index, keyword in enumerate(keywords):
            data = {
                'keyword':keyword,
                'result':crawler.get_info_by_keyword(keyword=keyword, limit=5, sleep_sec=0.2)
            }
            print(f'{index}   {data}')
            result.append(data)
    return result