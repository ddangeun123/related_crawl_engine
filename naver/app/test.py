import requests
import time
import asyncio
import aiohttp

async def send_request(session, request_url:str, keyword:str):
    async with session.get(f'{request_url}?keywords={keyword}') as response:
        return await response.text()

async def test():
    query = ['컴퓨터', '노트북', '키보드', '마우스']
    request_url = 'http://localhost:8001/search/navershopping'

    async with aiohttp.ClientSession() as session:
        for keyword in query:
            response = await send_request(session, request_url, keyword)
            print(response)  # 응답 코드를 출력합니다. 필요에 따라 변경하거나 제거할 수 있습니다.
        await asyncio.sleep(20)  # 20초 동안 대기합니다.

if __name__ == '__main__':
    asyncio.run(test())