import threading
import time


def boil_milk():
    print("Boiling milk....")
    time.sleep(2)
    print("Milk boiled....")


def toast_bun():
    print("Toasting the bun...")
    time.sleep(3)
    print("Done with the bun toast...")


t1 = threading.Thread(target=boil_milk)
t2 = threading.Thread(target=toast_bun)

start = time.time()
t1.start()
t2.start()
t1.join()
t2.join()
end = time.time()

print(f"Time taken: {end-start:.3f}")
