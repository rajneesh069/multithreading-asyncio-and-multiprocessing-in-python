import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


def check_stock(item):
    print("worker: checking stock for", item)
    time.sleep(3)  # blocking work on a worker thread
    return f"Stock items for {item} = 42"


async def async_work():
    print("async: starting short async sleep")
    await asyncio.sleep(2)
    print("async: finished sleep")


async def main():
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        # Create coroutine that runs the blocking function in a worker thread
        blocking_coro = loop.run_in_executor(pool, check_stock, "Masala Chai")
        # Create coroutine that does async sleep
        async_coro = async_work()
        # Run both concurrently, wait for both to finish
        blocking_res, _ = await asyncio.gather(blocking_coro, async_coro)
        print("main: blocking result ->", blocking_res)


async def main2():
    # for fine grained control over tasks, use asyncio.create_task() or else calling it directly inside asyncio.gather() is fine
    blocking_coro = asyncio.create_task(asyncio.to_thread(check_stock, "Masala Chai"))

    results = await asyncio.gather(blocking_coro, async_work())
    print("results:", results)


asyncio.run(main2())
