from fastapi import FastAPI, HTTPException
from driver_manager import DriverManager
from selenium_driver import SeleniumDriver
from scraper import Scraper
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
from starlette.concurrency import run_in_threadpool
import traceback
import time

from requests.exceptions import RequestException


app = FastAPI()
driver_manager = DriverManager()

driver_pool = ThreadPoolExecutor(max_workers=5)
drivers = [SeleniumDriver().set_up() for _ in range(5)]
for driver in drivers:
    driver_pool.submit(lambda: driver)

response_count = 0

async def get_driver():
    try:
        driver_future = driver_pool.submit(lambda: drivers.pop())
        return await run_in_threadpool(driver_future.result)
    except IndexError:
        driver = SeleniumDriver().set_up()
        drivers.append(driver)
        driver_future = driver_pool.submit(lambda: drivers.pop())
        return await run_in_threadpool(driver_future.result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/naver")
async def search_naver(keywords: str):
    try:
        global response_count
        if not keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        keywords = unquote(keywords, encoding='utf-8')
        driver = await get_driver()
        scraper = Scraper(driver=driver)

        result = await naver_task(keywords, scraper)

        return result
    except RequestException:
        time.sleep(3)
        result = await search_naver(keywords)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        drivers.append(driver)

async def naver_task(keywords: str, scraper: Scraper):
    global response_count
    try:
        response_count += 1
        result, driver = scraper.scrape_naver(keyword=keywords, delay=0.5)
        drivers.append(driver)
        return result
    except Exception as e:
        scraper.driver = SeleniumDriver().restart_driver(scraper.driver)
        result, driver = scraper.scrape_naver(keyword=keywords, delay=0.5)
        drivers.append(driver)
        return result
    finally:
        # if response_count > 30:
        #     scraper.driver = SeleniumDriver().restart_driver(scraper.driver)
        #     response_count = 0
        #     drivers.append(scraper.driver)
        pass

@app.get("/search/navershopping")
async def search_navershopping(keywords: str):
    try:
        global response_count
        if not keywords:
            raise HTTPException(status_code=400, detail="No keywords provided")
        keywords = unquote(keywords, encoding='utf-8')
        driver = await get_driver()
        scraper = Scraper(driver=driver)

        return await shopping_task(keywords, scraper=scraper)
    except Exception as e:
        try:
            driver = None
            scraper = None
            time.sleep(3)
            driver = await get_driver()
            scraper = Scraper(driver=driver)
            result = await shopping_task(keywords, scraper=scraper)
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        drivers.append(driver)

async def shopping_task(keywords:str, scraper: Scraper):
    global response_count
    try:
        response_count += 1
        result, driver = scraper.scrape_navershopping(keyword=keywords, delay=0.5)
        drivers.append(driver)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # if response_count > 30:
        #     scraper.driver =SeleniumDriver().restart_driver(scraper.driver)
        #     response_count = 0
        #     driver = scraper.driver
        pass