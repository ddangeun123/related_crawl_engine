from fastapi import FastAPI, HTTPException
from driver_manager import DriverManager
from scraper import Scraper
from urllib.parse import unquote


app = FastAPI()
driver_manager = DriverManager()
scraper = Scraper(driver=driver_manager.driver, driver_manager=driver_manager)

response_count = 0

@app.get("/search/naver")
async def search_naver(keywords: str):
    global response_count
    if not keywords:
        raise HTTPException(status_code=400, detail="No keywords provided")
    keywords = unquote(keywords, encoding='utf-8')

    try:
        response_count += 1
        result, scrape_success = scraper.scrape_naver(keyword=keywords, delay=0.5)
        return result
    except Exception as e:
        driver_manager.restart_driver(scraper.driver)
        result, scrape_success = scraper.scrape_naver(keyword=keywords, delay=0.5)
        return result
    finally:
        if response_count > 30:
            scraper.driver = driver_manager.restart_driver(scraper.driver)
            response_count = 0

@app.get("/search/navershopping")
async def search_navershopping(keywords: str):
    global response_count
    if not keywords:
        raise HTTPException(status_code=400, detail="No keywords provided")
    keywords = unquote(keywords, encoding='utf-8')

    try:
        response_count += 1
        result, scrape_success = scraper.scrape_navershopping(keyword=keywords, delay=0.5)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if response_count > 30:
            scraper.driver =driver_manager.restart_driver(scraper.driver)
            response_count = 0
