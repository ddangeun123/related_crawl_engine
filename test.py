import youtube_crawler

y = youtube_crawler.Youtube()

res = y.get_info_by_keyword("사과", 10, 1.5)
print(res)
