import threading

lockA = threading.Lock()
lockB = threading.Lock()


def fn1():
    with lockA:
        print("fn1 acquired lockA")
        with lockB:
            print("fn1 acquired lockB")


def fn2():
    with lockB:
        print("fn2 acquired lockB")
        with lockA:
            print("fn2 acquired lockA")


t1 = threading.Thread(target=fn1)
t2 = threading.Thread(target=fn2)

t1.start()
t2.start()
