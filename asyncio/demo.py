import asyncio


async def print_tick():
    loop = (
        asyncio.get_running_loop()
    )  # gets the same event loop started by asyncio.run(main()) below
    start = loop.time()
    # The monotonic clock time (in seconds) used internally by the event loop -  this is what is returned by loop.time().
    # loop.time() = “How much time has passed since the loop’s reference point?”
    tick = 0
    while tick < 10:
        print(f"[tick {tick}] loop time = {loop.time() - start:.3f}s")
        tick += 1
        await asyncio.sleep(0.2)


async def busy_worker(name, delay):
    print(f"{name}: started, will sleep {delay}")
    # This yields control to the loop while sleeping
    await asyncio.sleep(delay)
    print(f"{name}: done")


async def main():
    w1 = asyncio.create_task(busy_worker("Worker-A", 1.0))
    w2 = asyncio.create_task(busy_worker("Worker-B", 1.0))
    await print_tick()  # yields control to the loop!
    await asyncio.gather(w1, w2)  # same!


result = asyncio.run(main())  # creates a fresh event loop and starts it = while True

# asyncio.run(main()) does the following:

# 1. ✅ Creates a brand-new event loop (fresh and isolated — ignores any existing ones).
# 2. 🌀 Sets it as the current loop (accessible via asyncio.get_running_loop()).
# 3. 🚀 Runs the given coroutine (main()) until it’s fully complete.
#    - That means it awaits everything inside it, including nested coroutines and tasks.
# 4. 💣 Closes the loop after completion (no leftover tasks or open handles).
# 5. 🎁 Returns whatever value the coroutine returns — just like `await` would.

# ⚠️ IMPORTANT:
# If an event loop is already running in the same thread,
# asyncio.run() will raise RuntimeError — it won’t cancel or reuse that loop.
