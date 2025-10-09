import time
import aiohttp
import asyncio


async def fetch(
    session,
    url,
):
    async with session.get(url=url) as response:
        print(f"Fetched {url} with status: {response.status}")


async def main():
    urls = ["https://httpbin.org/delay/2"] * 3
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session=session, url=url) for url in urls]
        await asyncio.gather(*tasks)


start = time.time()
asyncio.run(main())
end = time.time()
print(f"Total time taken: {end-start:.3f}s")
