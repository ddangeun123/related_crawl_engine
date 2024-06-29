

def _api_search_page(self, keyword: str):
        try:
            res = requests.get(
                f"https://www.youtube.com/results?search_query={keyword}",
                headers={
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "accept-language": "ko-KR,ko;q=0.9",
                    "content-type": "text/html; charset=utf-8",
                },
            )

            if res.status_code != 200:
                raise Exception("stauts code error")
            
            return res.content.decode("utf-8")
        except:
            # raise Exception("api 실패")
            self._api_search_page(keyword=keyword)