import threading
import asyncio
import time


def background_worker():
    while True:
        print("Logging system health: 🕰️")
        time.sleep(1)


async def fetch_order():
    await asyncio.sleep(4)
    print("🎁 order fetched")


threading.Thread(target=background_worker, daemon=True).start()
asyncio.run(fetch_order())
