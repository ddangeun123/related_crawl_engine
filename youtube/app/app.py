from fastapi import FastAPI
from crawler import Crawler

import re
import time

app = FastAPI()
crawler = Crawler()

@app.get("/search/youtube")
async def search_youtube(keywords: str):
    keywords = keywords.split(',')
    result = []
    for index, keyword in enumerate(keywords):
        data = {
            'keyword':keyword,
            'result':crawler.get_info_by_keyword(keyword=keyword, limit=250, sleep_sec=0.2)
        }
        print(f'{index}   {data}')
        result.append(data)
    if len(result) == 0 :
        for index, keyword in enumerate(keywords):
            data = {
                'keyword':keyword,
                'result':crawler.get_info_by_keyword(keyword=keyword, limit=250, sleep_sec=0.2)
            }
            print(f'{index}   {data}')
            result.append(data)
    return result