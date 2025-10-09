import asyncio
import time


async def brew_chai(name: str):
    print(f"Brewing {name} tea....")
    await asyncio.sleep(3)
    print(f"{name} tea has been brewed")


async def main():
    await asyncio.gather(brew_chai("Masala"), brew_chai("Green"), brew_chai("Lemon"))


start = time.time()
asyncio.run(main())
end = time.time()
print(f"Time taken to brew: {end-start:.3f}s")
