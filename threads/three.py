import threading


counter = 0
lock = threading.Lock()


def increment():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1


threads = [threading.Thread(target=increment) for _ in range(10)]

[t.start() for t in threads]
[t.join() for t in threads]

print("counter value:", counter)

name = "Rajneesh Mishra"


def print_name():
    name += 10
    print(name)


print_name()
