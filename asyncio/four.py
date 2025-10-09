from concurrent.futures import ProcessPoolExecutor
import asyncio
import time


def encrypt_data(data: str):
    for _ in range(10_000_000):
        pass  # CPU bound work
    encrypted_data = data[::-1]
    return f"🔒{encrypted_data}"


async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, encrypt_data, "rajneesh")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
