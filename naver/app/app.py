from fastapi import FastAPI, HTTPException
from driver_manager import DriverManager
from scraper import Scraper
import re
import time

app = FastAPI()
driver_manager = DriverManager()
scraper = Scraper(driver=driver_manager.driver, driver_manager=driver_manager)

response_count = 0

@app.get("/search/naver")
async def search_naver(keywords: str):
    global response_count
    try:
        response_count += 1
        result = scraper.scrape_naver(keyword=keywords, delay=0.5)
        return result
    except Exception as e:
        driver_manager.restart_driver(scraper.driver)
        result = scraper.scrape_naver(keyword=keywords, delay=0.5)
        return result
    finally:
        if response_count > 30:
            scraper.driver = driver_manager.restart_driver(scraper.driver)
            response_count = 0

@app.get("/search/navershopping")
async def search_navershopping(keywords: str):
    global response_count
    try:
        response_count += 1
        result = scraper.scrape_navershopping(keyword=keywords, delay=0.5)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if response_count > 30:
            scraper.driver =driver_manager.restart_driver(scraper.driver)
            response_count = 0
