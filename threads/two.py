import threading
import time
import requests


def download_file(url: str) -> None:
    resp = requests.get(url=url)
    print(len(resp.content), "bytes downloaded")


start = time.time()
threads: list[threading.Thread] = []
urls = [
    "https://httpbin.org/image/jpeg",
    "https://httpbin.org/image/png",
    "https://httpbin.org/image/svg",
]

for url in urls:
    t = threading.Thread(target=download_file, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

end = time.time()

print(f"time taken in multithreading: {end-start:.3f}s", end="\n\n")


start_sync = time.time()
for url in urls:
    download_file(url=url)

end_sync = time.time()

print(f"time taken in sync: {end_sync-start_sync:.3f}s", end="\n\n")
