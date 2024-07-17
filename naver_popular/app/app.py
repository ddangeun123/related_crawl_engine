from fastapi import FastAPI
from driver_manager import DriverManager
from scraper import Scraper
from urllib3.exceptions import TimeoutError, MaxRetryError

import logging
from datetime import datetime
import re
import time

app = FastAPI()
driver_manager = DriverManager()
scraper = Scraper(driver=driver_manager.driver, driver_manager=driver_manager)

response_count = 0

@app.get("/search/naver/popular")
async def search_naver_popular(keywords: str):
    global response_count
    try:
      response_count += 1
      result = scraper.scrape_naver_popular(keyword=keywords, delay=0.5)
      print(result)
      return result
    except MaxRetryError:
      driver_manager.restart_driver(scraper.driver)

      data = {
          'keyword': keywords,
          'popular_contents': '인기 주제가 없습니다.'
      }
      return data
    except Exception as e:
      driver_manager.restart_driver(scraper.driver)
      result = scraper.scrape_naver_popular(keyword=keywords, delay=0.5)
      print(result)
      return result
    
    finally:
      if response_count > 30:
        scraper.driver = driver_manager.restart_driver(scraper.driver)
        response_count = 0

@app.middleware("http")
async def log_requests(request, call_next):
    # Get the current logger
    logger = logging.getLogger('uvicorn')
    
    # Remove all handlers from the logger
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Get the current date and create a log file name
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'app-{current_date}.log'
    
    # Create a new handler with the new log file name
    handler = logging.FileHandler(log_filename, 'a')
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    
    # Add the new handler to the logger
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    ip_address = request.client.host
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url} from IP: {ip_address} at {request_time}")
    response = await call_next(request)
    end_time = time.time()
    duration_time = round(end_time - start_time, 2)  # 소수점 두 자리까지 반올림
    logger.info(f"{request.method} {request.url} from IP : {ip_address} at Outgoing response: {response.status_code} Duration : {duration_time} seconds")
    
    return response
