import sys
import json
import requests

from bs4 import BeautifulSoup

class YoutubeAPI:
    def __init__(self):
        self.click_tracking_params = ""
        self.continuation_command = ""
        self.api_key = ""
        self.post_json = {
            "continuation": "",
            "context": {},
        }

        self.detail_json = {
            "contentCheckOk": False,
            "context": {},
            # 넣기
            "params": "",
            "playbackContext": {
                "contentPlaybackContext": {
                    "autoCaptionsDefaultOn": False,
                    "autonav": False,
                    "autonavState": "STATE_NONE",
                    "autoplay": True,
                    # 넣기
                    "currentUrl": "",
                    "html5Preference": "HTML5_PREF_WANTS",
                    "lactMilliseconds": "-1",
                    # 넣기
                    "referer": "",
                    "signatureTimestamp": 19590,
                    "splay": False,
                    "vis": 5,
                },
                "watchAmbientModeContext": {
                    "hasShownAmbientMode": True,
                    "watchAmbientModeEnabled": True,
                },
            },
            "racyCheckOk": False,
            # 넣기
            "videoId": "",
        }
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

    def logic_test(self):
            # first page api 요청
            res = self._api_search_page(keyword="떡볶이")

            # api key 가져오기
            api_key_raw_start = res.find("INNERTUBE_API_KEY")
            api_key_raw = res[api_key_raw_start : api_key_raw_start + 130]
            startPoint = api_key_raw.find(":")
            endPoint = api_key_raw.find(",")
            self.api_key = api_key_raw[startPoint + 2 : endPoint - 1]

            # 설정파일 만들기.
            startPoint = res.find("INNERTUBE_CONTEXT") + 2 + len("INNERTUBE_CONTEXT")
            endPoint = res.find("INNERTUBE_CONTEXT_CLIENT_NAME") - 2
            config_data_raw = res[startPoint:endPoint]
            config_data = json.loads(config_data_raw)
            # context에 넣기
            self.post_json["context"] = config_data
            self.detail_json["context"] = config_data
            # 결과 json으로 변형
            initial_data = res.split("ytInitialData = ")[1]
            splited = initial_data.split(";</script>")
            initial_data_json_raw = splited[0]
            initial_data_json = json.loads(initial_data_json_raw)

            # 다음 페이지 정보 가져오기
            try:
                next_page_info_contents = initial_data_json["contents"][
                    "twoColumnSearchResultsRenderer"
                ]["primaryContents"]["sectionListRenderer"]["contents"]
                try:
                    next_page_info_json = next_page_info_contents[-1][
                        "continuationItemRenderer"
                    ]
                except:
                    next_page_info_json = next_page_info_contents[2][
                        "continuationItemRenderer"
                    ]
            except Exception as e:
                print(f"예기치 못한 에러 \n 에러코드 : {sys.exc_info.__name__}", e)
                next_page_info_json = {}

            # 값 넣어주기
            is_break = False
            try:
                self.click_tracking_params = next_page_info_json[
                    "continuationEndpoint"
                ]["clickTrackingParams"]
                self.continuation_command = next_page_info_json["continuationEndpoint"][
                    "continuationCommand"
                ]["token"]
                self.post_json["continuation"] = self.continuation_command
            except:
                self.click_tracking_params = ""
                self.continuation_command = ""
                is_break = True

            # 데이터 가공
            youtube_list_json = initial_data_json["contents"][
                "twoColumnSearchResultsRenderer"
            ]["primaryContents"]["sectionListRenderer"]["contents"][0][
                "itemSectionRenderer"
            ][
                "contents"
            ]
            pass
            # 유튜브 리스트 json 저장
            with open("youtube_list.json", 'w') as json_file:
                json.dump(youtube_list_json, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    api = YoutubeAPI()
    api.logic_test()
    pass