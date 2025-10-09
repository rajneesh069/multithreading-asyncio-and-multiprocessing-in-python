import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


def check_stock(item):
    print(f"Checking stock for {item}")
    time.sleep(3)
    return f"Stock items for {item} = 42"


async def main():
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        # puts the blocking stuff on another thread so that the event loop remains "unblocked by blocking code"
        result = await loop.run_in_executor(pool, check_stock, "Masala Chai")
        print(result)


asyncio.run(main())
