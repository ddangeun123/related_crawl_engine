import requests
import threading
from collections import Counter

def send_request(ip_address, counter, lock):
    for _ in range(10):  # 각 스레드당 20,000번의 요청을 2로 나누어 10,000번씩 실행
        try:
            response = requests.get(f"http://{ip_address}/search/youtube?keywords=%ED%94%84%EB%A1%9C%ED%8B%B4&limit=300")
            with lock:
                counter[response.status_code] += 1
        except Exception as e:
            with lock:
                counter['fail'] += 1
            print(f"Request failed: {e}")

# 상태 코드 카운터와 락 초기화
counter = Counter()
lock = threading.Lock()

# 스레드 리스트 생성
threads = []

# 2개의 스레드 생성 및 시작
for _ in range(2):
    thread = threading.Thread(target=send_request, args=("223.130.160.196:8001", counter, lock))
    thread.start()
    threads.append(thread)

# 모든 스레드가 종료될 때까지 대기
for thread in threads:
    thread.join()

# 상태 코드별 카운트 출력
print("Status Code Counts:")
for status_code, count in counter.items():
    print(f"{status_code}: {count}")