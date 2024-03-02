from fastapi import FastAPI
from driver_manager import DriverManager
from crawler import Crawler
from scraper import Scraper
import re
import time

app = FastAPI()
crawler = Crawler()
driver_manager = DriverManager()
scraper = Scraper(driver=driver_manager.driver, driver_manager=driver_manager)

response_count = 0

@app.get("/search/google")
async def search_google(keywords: str):
    global response_count
    try:
        response_count += 1
        result = scraper.scrape_google(keyword=keywords, delay=0.5)
        print(result)
        return result
    except Exception as e:
        driver_manager.restart_driver(scraper.driver)
        result = scraper.scrape_google(keyword=keywords, delay=0.5)
        print(result)
        return result
    finally:
        if response_count > 20:
            scraper.driver = driver_manager.restart_driver(scraper.driver)
            response_count = 0