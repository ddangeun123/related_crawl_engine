import requests
import json
import time


class Youtube:
    def __init__(self):
        self.click_tracking_params = ""
        self.continuation_command = ""
        self.api_key = ""
        self.post_json = {
            "continuation": "",
            "context": {},
        }

    def get_info_by_keyword(self, keyword: str, limit: int, sleep_sec: float = 1.5):
        try:
            # first page api 요청
            res = self._api_search_page(keyword=keyword)

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

            # 결과 json으로 변형
            initial_data = res.split("ytInitialData = ")[1]
            splited = initial_data.split(";</script>")
            initial_data_json_raw = splited[0]
            initial_data_json = json.loads(initial_data_json_raw)

            # 다음 페이지 정보 가져오기
            try:
                next_page_info_json = initial_data_json["contents"][
                    "twoColumnSearchResultsRenderer"
                ]["primaryContents"]["sectionListRenderer"]["contents"][1][
                    "continuationItemRenderer"
                ]
            except:
                next_page_info_json = {}

            # 값 넣어주기
            self.click_tracking_params = next_page_info_json["continuationEndpoint"][
                "clickTrackingParams"
            ]
            self.continuation_command = next_page_info_json["continuationEndpoint"][
                "continuationCommand"
            ]["token"]
            self.post_json["continuation"] = self.continuation_command

            # 데이터 가공
            youtube_list_json = initial_data_json["contents"][
                "twoColumnSearchResultsRenderer"
            ]["primaryContents"]["sectionListRenderer"]["contents"][0][
                "itemSectionRenderer"
            ][
                "contents"
            ]

            # 결과 초기화
            result = []
            limit_count = limit

            for detail in youtube_list_json:
                if "videoRenderer" not in detail:
                    continue

                if limit_count == 0:
                    break

                video_id = detail["videoRenderer"]["videoId"]

                try:
                    chhannel_name = detail["videoRenderer"]["ownerText"]["runs"][0][
                        "text"
                    ]
                except:
                    chhannel_name = ""

                try:
                    title = detail["videoRenderer"]["title"]["runs"][0]["text"]
                except:
                    title = ""
                # 조회수
                try:
                    view_count = detail["videoRenderer"]["viewCountText"]["simpleText"]
                except:
                    view_count = ""

                # 발행일
                try:
                    published_at = detail["videoRenderer"]["publishedTimeText"][
                        "simpleText"
                    ]
                except:
                    published_at = ""

                # 상세보기

                try:
                    detail = detail["videoRenderer"]["detailedMetadataSnippets"][0][
                        "snippetText"
                    ]["runs"][0]["text"]
                except:
                    detail = ""

                limit_count -= 1

                result.append(
                    {
                        "video_id": video_id,
                        "title": title,
                        "view_count": view_count,
                        "published_at": published_at,
                        "detail": detail,
                        "chhannel_name": chhannel_name,
                    }
                )

            while limit_count > 0:
                time.sleep(sleep_sec)

                # 다음 페이지 가져오기
                initial_data_json = self._api_search_page_next(self.api_key)

                # 다음 페이지를 위한 파라메터 저장
                self.click_tracking_params = initial_data_json[
                    "onResponseReceivedCommands"
                ][0]["clickTrackingParams"]

                self.continuation_command = initial_data_json[
                    "onResponseReceivedCommands"
                ][0]["appendContinuationItemsAction"]["continuationItems"][1][
                    "continuationItemRenderer"
                ][
                    "continuationEndpoint"
                ][
                    "continuationCommand"
                ][
                    "token"
                ]

                self.post_json["continuation"] = self.continuation_command

                # 데이터 가져오기
                youtube_list_json = initial_data_json["onResponseReceivedCommands"][0][
                    "appendContinuationItemsAction"
                ]["continuationItems"][0]["itemSectionRenderer"]["contents"]

                for detail in youtube_list_json:
                    if "videoRenderer" not in detail:
                        continue

                    if limit_count == 0:
                        break

                    video_id = detail["videoRenderer"]["videoId"]

                    title = detail["videoRenderer"]["title"]["runs"][0]["text"]
                    # 조회수
                    view_count = detail["videoRenderer"]["viewCountText"]["simpleText"]

                    # 발행일
                    published_at = detail["videoRenderer"]["publishedTimeText"][
                        "simpleText"
                    ]

                    try:
                        chhannel_name = detail["videoRenderer"]["ownerText"]["runs"][0][
                            "text"
                        ]
                    except:
                        chhannel_name = ""

                    try:
                        detail = detail["videoRenderer"]["detailedMetadataSnippets"][0][
                            "snippetText"
                        ]["runs"][0]["text"]
                    except:
                        detail = ""

                    limit_count -= 1
                    result.append(
                        {
                            "video_id": video_id,
                            "title": title,
                            "view_count": view_count,
                            "published_at": published_at,
                            "detail": detail,
                            "chhannel_name": chhannel_name,
                        }
                    )

            return result

        except Exception as e:
            raise e

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
            raise Exception("api 실패")

    def _api_search_page_next(self, key: str):
        try:
            res = requests.post(
                f"https://www.youtube.com/youtubei/v1/search?key={key}&prettyPrint=false",
                headers={
                    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "accept-language": "ko-KR,ko;q=0.9",
                    "content-type": "application/json; charset=UTF-8",
                },
                json=self.post_json,
            )

            if res.status_code != 200:
                raise Exception("stauts code error")

            return json.loads(res.content)
        except:
            raise Exception("api 실패")
