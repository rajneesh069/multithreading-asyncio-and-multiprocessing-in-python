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

# Event Loop Pseudo Code

- run ready → run timers → run I/O events → repeat

```python
while True:
    run_ready_callbacks()
    run_due_timers()
    poll_io_events()
    add ready I/O callbacks to READY queue
```

- “Next event loop tick” = the next moment the event loop gets CPU time after your coroutine yields or finishes the current line of code = **next iteration of the loop**

# More on asyncio

- Calling an `async def` does NOT run its body. It only creates a coroutine object.

```python
async def check_status(rtn_prd):
    return await loop.run_in_executor(
        None,
        lambda: file_download_status(
            rtn_prd=rtn_prd,
        ),
    )

tasks = [check_status(p) for p in request.rtn_prd] # This only creates coroutine objects.
# It does NOT run:

# any code inside check_status

# definitely does NOT run await loop.run_in_executor

# Nothing inside executes until the event loop actually schedules them.
results = await asyncio.gather(*tasks) # Parallel "execution"
```

### Why doesn’t `check_status(p)` immediately call `await`?

Because:

- `check_status` is defined using `async def`

- Calling an `async def` returns a coroutine object

- A coroutine object is “paused at the first line”

- It does not start executing until you do one of the following:

  - `await check_status(p)`

  - `asyncio.create_task(check_status(p))`

  - `asyncio.gather(check_status(p))`

  - the event loop resumes it for any reason

### When do they actually run?

When you do:

```python
results = await asyncio.gather(*tasks)
```

Now here's what happens:

1. gather takes each coroutine

2. Schedules all of them in the event loop immediately

3. Starts running them concurrently

4. Each coroutine enters the body of check_status

5. They finally hit:

```python
await loop.run_in_executor(...)
```

**That is the FIRST moment any of the executor code actually executes.**

✔️ So the flow in above case is:

1. Define async function
   ```python
   async def check_status(...): # doesn't run anything
   ```
2. Call the async function → creates coroutine object

   ```python
   coro = check_status(p) # still doesn't run anything
   ```

3. Event loop runs them through gather

   ```python
   await asyncio.gather(coro1, coro2, coro3)
   ```

4. Now the body executes

   ```python
   return await loop.run_in_executor(...)
   ```

5. The run_in_executor submits work to the threadpool

   - This is scheduled immediately in the threadpool

   - But the coroutine pauses waiting for the thread result

   - Meanwhile, other coroutines run — giving you concurrency

## [Parallel v Sequential Execution in asyncio](./parallel-v-sequential.py)

### **1. `await`**

👉 _Wait for a coroutine/future to finish. Makes execution SEQUENTIAL at that point._

---

### **2. `asyncio.gather(*coros)`**

👉 _Run multiple coroutines CONCURRENTLY and wait for all of them._

---

### **3. `asyncio.create_task(coro)`**

👉 _Schedule a coroutine to run in the background (fire-and-forget). Runs CONCURRENTLY._

---

### **4. `asyncio.to_thread(func, *args)`**

👉 _Run a blocking function in a thread. Returns a coroutine you must await. Runs CONCURRENTLY across threads._

---

### **5. `loop.run_in_executor(executor, func, *args)`**

👉 _Lower-level version of `to_thread`. Runs blocking code in threads or processes._

---

### **6. `asyncio.sleep(x)`**

👉 _Yield to event loop for x seconds. Doesn’t block the loop._

---

### **7. `asyncio.wait_for(coro, timeout)`**

👉 _Run a coroutine with timeout enforcement._

---

### **8. `asyncio.Semaphore(n)`**

👉 _Limit concurrency — useful when hitting APIs or databases._

---

## ⚡ When is execution **parallel**, **concurrent**, or **sequential**?

### ✔️ **Sequential**

You get sequential behavior when you do:

#### **Using `await` inside a loop**

```python
for p in items:
    result = await check(p)   # waits one-by-one
```

#### **Calling blocking code directly**

```python
result = some_heavy_cpu_func()   # blocks everything
```

---

## ✔️ **Concurrent (async coroutines)**

Coroutines run _overlapping in time_ (not literally parallel CPU threads unless using threads or processes).

### **Using `asyncio.gather`**

```python
await asyncio.gather(check(a), check(b), check(c))
```

### **Using `asyncio.create_task`**

```python
task = asyncio.create_task(check(x))
# (you don't await — it runs concurrently)
```

---

## ✔️ **Parallel (actual threads or processes)**

Happens when you offload blocking work.

### **Using `asyncio.to_thread`**

```python
await asyncio.to_thread(blocking_func)
```

### **Using `run_in_executor`**

```python
await loop.run_in_executor(None, blocking_func)
```

### **Using `ProcessPoolExecutor`**

```python
await loop.run_in_executor(process_pool, cpu_heavy_func)
```

---

# 🧠 TL;DR

- **`await` inside a loop → sequential**
- **`gather` → concurrent**
- **`create_task` → fire-and-forget concurrent**
- **`to_thread` / `run_in_executor` → parallel threads**
- **CPU work → use processes for true parallelism**
- **Blocking sync code → stick it in `to_thread`**

# JS vs Python Comparison

## 🧠 First: The JS World

### **JavaScript has two named queues:**

| JS Queue            | Meaning                                            |
| ------------------- | -------------------------------------------------- |
| **Microtask queue** | Promises, `async/await`, `.then()` callbacks       |
| **Macrotask queue** | `setTimeout`, `setInterval`, I/O events, UI events |

Event loop order: **Run microtask queue → then macrotask → repeat**

---

## 🐍 Python World: Similar concepts, **different names**

Python (asyncio) event loop has **the same conceptual split**, but they are NOT called micro/macro tasks.

Instead, Python has these “named queues / structures”:

---

# 📌 **1. Ready Queue** _(“callbacks ready to run now”)_

This is the closest to **JS microtask queue**.

Contains:

- Tasks that just became ready after an `await`
- Callbacks scheduled via `loop.call_soon`
- Callbacks from completed Futures
- Tasks resumed from I/O events

Think of `ready` as:

> “Everything the loop should run immediately, before it does anything else.”

---

# 📌 **2. Scheduled Calls Queue (Timer Queue)**

This is a **min-heap (priority queue)** of timed callbacks.

Equivalent to **JS macrotask setTimeout**.

Contains:

- `loop.call_later(delay, callback)`
- `loop.call_at(timestamp, callback)`
- Sleep wakeups (`await asyncio.sleep(...)`)
- Timeout events

This queue determines **future callbacks** based on time.

---

# 📌 **3. I/O Selector (I/O event queue)**

This is the **epoll / kqueue / I/O multiplexer** layer.

Contains:

- Socket read readiness
- Socket write readiness
- Pipe, file-descriptor, network events

Equivalent to:

> “macrotasks triggered by I/O events” in JS.

When an I/O event is ready, the event loop puts the corresponding task into the **Ready Queue**.

---

# 📌 **4. Executor Thread/Process Callback Queue**

When you use:

- `asyncio.to_thread`
- `loop.run_in_executor`
- ProcessPoolExecutor

The result of the thread/process comes back through a special callback:

> “Executor result ready → put a callback into **Ready Queue**.”

JS equivalent:

- Worker threads returning results via event loop

---

# 📌 **5. Task Objects internally manage their own state**

While not a queue, each `Task` individually manages:

- PENDING
- RUNNING
- SCHEDULED
- FINISHED
- CANCELLED

A Task becomes runnable and enters the **Ready Queue** whenever its awaited thing completes.

---

# 🎯 Summary Table (JS vs Python Queues)

| Concept                            | JS Name                | Python Name                            | Notes                              |
| ---------------------------------- | ---------------------- | -------------------------------------- | ---------------------------------- |
| Tasks that must run ASAP           | **Microtask Queue**    | **Ready Queue**                        | Includes resumed coroutine steps   |
| Delayed callbacks                  | **Macrotask (timers)** | **Scheduled Calls Queue (timer heap)** | Same concept                       |
| Network / file I/O                 | **Macrotask (I/O)**    | **I/O selector / poller**              | When ready → goes into Ready Queue |
| Background threads/process results | Worker callbacks       | Executor callback queue → Ready Queue  |                                    |
| Promises                           | Promise microtasks     | Future callbacks → Ready Queue         |                                    |

---

# 📌 **Python event loop flow (simplified)**

```python
while True:
    run_ready_callbacks()
        ↓
        If one of these tasks hits `await`,
        it is SUSPENDED and removed from ready queue.
        Loop DOES NOT immediately jump to next steps.
        It simply finishes processing current ready callback,
        then proceeds:

    run_due_timers()
        - check if any timer expired (e.g. sleep finished)
        - if yes → put those callbacks into READY queue

    poll_io_events()
        - check sockets, file descriptors
        - if ready → put those callbacks into READY queue

    (loop back)

```

## Analogy

```python
Task A running...
Task A hits await something
    → Task A pauses
    → Task A is moved to "waiting list"
    → Event loop takes control back
Event loop:
    - resumes Task B from ready queue
    - resumes Task C
    - checks timers
    - checks I/O sockets
    - when "something" is done, task A is moved back to ready queue
Event loop picks Task A → resumes where it left off
```

JS:

```
run microtasks → run macrotasks → repeat
```

Python:

```
run ready → run timers → run I/O events → repeat
```

## What does `await`ing something means?

```
await something
↓
move coroutine to waiting state
↓
event loop runs other ready tasks, timers, I/O
↓
when awaited future is done, put coroutine back into READY queue
↓
resume it at next event loop tick

```

---

# 🧨 Why Python doesn't have explicit micro/macro task vocabulary?

Because:

- Python exposes the **coroutines**, not the queue semantics
- You control scheduling via `await`, `create_task`, and timers
- The loop’s queues exist internally, not conceptually for devs

But the behavior is nearly identical.

---

| “Queue Type”                   | JS Name           | Python Equivalent                    | When It's Used                                           |
| ------------------------------ | ----------------- | ------------------------------------ | -------------------------------------------------------- |
| **Immediate / next tick work** | Microtask queue   | **Ready queue**                      | Awaited coroutines resuming, FUTURE callbacks, call_soon |
| **Timed work**                 | Macrotask (timer) | **Scheduled calls heap**             | sleep, call_later, timeouts                              |
| **I/O work**                   | Macrotask (I/O)   | **I/O selector / poller**            | Sockets, network events                                  |
| **Thread / process results**   | Worker callback   | **Executor callbacks → Ready queue** | to_thread, run_in_executor                               |

---
