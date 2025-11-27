import asyncio
import time


def job():
    time.sleep(3)


async def k():
    print("Hello")


async def main():
    loop = asyncio.get_running_loop()
    # this is sequential as you await the moment you "schedule" the coroutine
    start_time = time.time()
    r1 = await loop.run_in_executor(None, job)
    r2 = await loop.run_in_executor(None, job)
    end_time = time.time()
    print(f"Sequential claim time: {end_time - start_time:.3f}")

    # this is parallel
    f1 = loop.run_in_executor(None, job)
    f2 = loop.run_in_executor(None, job)
    start_time = time.time()
    r1 = await f1
    r2 = await f2
    end_time = time.time()
    print(f"Parallel claim time: {end_time - start_time:.3f}")

    # this is also parallel
    start_time = time.time()
    f1 = loop.run_in_executor(None, job)
    f2 = loop.run_in_executor(None, job)
    results = await asyncio.gather(*[f1, f2])
    end_time = time.time()
    print(f"My Parallel claim time: {end_time - start_time:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
