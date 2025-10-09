# Asyncio vs Multithreading vs Multiprocessing

| Concept               | What’s Really Happening                                                                                                                              | Key Rule                                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **`asyncio`**         | A _single-threaded_, cooperative multitasking system. One event loop, many coroutines. Each coroutine _yields_ with `await`, allowing others to run. | Don’t block the loop! Only use `await`-based or async-friendly functions (e.g., `await asyncio.sleep()`, not `time.sleep()`). |
| **`threading`**       | Multiple OS-level threads, each with its own GIL-managed execution context.                                                                          | Each thread can have its _own event loop_, but only one loop can run per thread.                                              |
| **`multiprocessing`** | Spawns _new Python interpreters_ (separate processes) with their own memory, GIL, and threads.                                                       | Processes communicate via IPC (e.g. `Queue`, `Pipe`, `Value`, shared memory). Perfect for CPU-bound work.                     |

```
[asyncio] single loop, single thread
├─ task 1 ─▶ await
├─ task 2 ─▶ await
└─ task 3 ─▶ await
↳ yields to scheduler, all on same core

[threading]
├─ thread 1: maybe runs asyncio loop
├─ thread 2: maybe blocking I/O
└─ thread 3: background worker
↳ All share same process memory, GIL-enforced switching

[multiprocessing]
├─ process 1: its own memory, GIL, and threads
├─ process 2: independent interpreter
└─ process 3: communicates via IPC (Queue, Pipe)
↳ True parallel execution on separate cores
```

# What to choose when

| Task Type                                              | Use This              | Why                                                                |
| ------------------------------------------------------ | --------------------- | ------------------------------------------------------------------ |
| I/O bound (HTTP calls, DB queries, waiting on sockets) | **`asyncio`**         | Non-blocking, single-threaded concurrency                          |
| CPU bound (math, encryption, parsing)                  | **`multiprocessing`** | True parallelism across cores                                      |
| Mixed / legacy blocking code                           | **`threading`**       | Integrates blocking code with async via `to_thread()` or executors |

# 🧠 Asyncio “Where to Await vs Not” Cheat Sheet

| Situation / Expression                                 | Should you `await`?                               | Notes / Memory Hook                                                                           |
| ------------------------------------------------------ | ------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `async def foo()` → `foo()`                            | ✅ Yes (or schedule via create_task)              | Calling an `async def` gives a coroutine object; you must await it to run it (or schedule it) |
| `asyncio.sleep(...)`                                   | ✅ Yes                                            | Sleep is async; await it to pause this coroutine without blocking the loop                    |
| `await asyncio.to_thread(blocking_fn, ...)`            | ✅ Yes                                            | Wrapping sync/blocking code in a thread; await the result                                     |
| `loop.run_in_executor(pool, blocking_fn, ...)`         | ✅ Yes                                            | Same idea as `to_thread` but with explicit executor                                           |
| `asyncio.create_task(coro())` → assigned to a variable | ❌ Not immediately                                | Scheduling for concurrency; you can await later if you want the result                        |
| `await asyncio.create_task(coro())`                    | ❌ Usually                                        | Redundant — you scheduled it just to immediately wait, same as `await coro()`                 |
| `asyncio.gather(coro1(), coro2(), ...)`                | ✅ Yes                                            | Waits for all coroutines concurrently; returns results in order                               |
| Fire-and-forget background task                        | ❌ Not now                                        | `asyncio.create_task(coro())` without awaiting → runs in background; track if needed          |
| `asyncio.as_completed([...])`                          | ✅ Inside a loop                                  | `await` each future as it finishes to process results incrementally                           |
| Sync function that **doesn’t block**                   | ❌ No                                             | Just call normally; no need to wrap or await                                                  |
| Sync function that **blocks** (e.g., `time.sleep`)     | ✅ Wrap in `to_thread` or `run_in_executor` first | Never `await` a pure blocking sync function — it will freeze the loop                         |
