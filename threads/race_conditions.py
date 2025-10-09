import threading

counter = 0


def fn():
    # no locks acquired
    global counter
    for _ in range(100):
        counter += 1


# proper way
lock = threading.Lock()


# correct way to use lock
def fn2():
    global counter
    for _ in range(200):
        with (
            lock
        ):  # put lock around the smallest unit of code which must NOT be corrupted by threads!
            counter += 1


t1 = threading.Thread(target=fn)
t2 = threading.Thread(target=fn)

t1.start()
t2.start()

print(f"counter: {counter}")
