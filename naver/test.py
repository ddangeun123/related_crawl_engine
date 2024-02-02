import requests
from urllib.parse import unquote, quote
import json
import time

def Send_request(keyword):
    base_url = 'http://localhost:8000/search/navershopping?'
    keywords = f'keywords={quote(keyword)}'
    try:
        res = requests.get(base_url+keywords)

        if res.status_code == 200:
            # results = extract_result(res.text)
            return res.text
        else:
            print(res.status_code)
            return None

    except Exception as e:
        print(e)

def extract_result(string):
    try:
        data = json.loads(string)

        results = [item['result'] for item in data]

        flattened_results = []
        for sublist in results:
            for result_item in sublist:
                if result_item == None:
                    continue
                flattened_results.append(result_item)

        return flattened_results
    except json.JSONDecodeError as e:
        pass
    except Exception as e:
        print(f"디코딩 에러 : {e}")
        return None


if __name__ == '__main__':
    max_loop = 10
    cur_loop = 0
    response = ""
    formatted_result = []
    keywords = '초콜릿,비스킷,빼빼로,초코,핫초코,제티,우유,밀크초콜릿'
    db_keywords = []

    while cur_loop < max_loop or response == None or len(formatted_result) <= 0:
        response = Send_request(keyword=keywords)
        if response is not None:
            formatted_result = list(set(extract_result(response)))
            # formatted_result = [ele_format for ele_format in formatted_result if ele_format not in db_keywords]
            # db_keywords = list(set(db_keywords.append(formatted_result)))
            print(formatted_result)
            cur_loop += 1
            keywords = str(formatted_result).replace("[", "").replace("]", "")
        time.sleep(1)
