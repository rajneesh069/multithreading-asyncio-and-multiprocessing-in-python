import threading
import time


def logger():
    while True:
        print("Logging something")
        time.sleep(1)


t = threading.Thread(
    target=logger, daemon=True
)  # daemon = False, keeps the thread running even if main thread finishes
# daemon = True, thread stops running as soons as main thread finishes
t.start()
print("Main thread finished.")
