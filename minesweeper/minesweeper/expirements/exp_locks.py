import threading
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class Counter:

    SLEEP_TIME = 0.025

    def __init__(self, start_count=0):
        self.count = start_count
        self.lock = threading.Lock()

    def __str__(self):
        with self.lock:
            return str(self.count)

    def increment(self, times=1):
        self.lock.acquire()

        for i in range(times):
            self.count += 1

        self.lock.release()

    def decrement(self, times=1):
        self.lock.acquire()

        for i in range(times):
            self.count -= 1

        self.lock.release()


class StringStretcher:
    """
    A StringStretcher object lengthens a string s by an increment i a specified number of times n.
    It can also shorten the string s.
    """
    SLEEP_TIME = 0.025

    def __init__(self, string, addition):
        self.string: str = string
        self.addition: str = addition
        self.lock = Lock()

    def __str__(self):
        with self.lock:
            return str(self.string)

    def __len__(self):
        with self.lock:
            return len(self.string)

    def increment(self, times=1):
        self.lock.acquire()

        for i in range(times):
            self.string += self.addition

        self.lock.release()

    def decrement(self, times=1):
        self.lock.acquire()

        for i in range(min(len(self.string), times)):
            self.string = self.string[:-1]

        self.lock.release()


def main():
    configs = {
        "threads": 50,
        "cycles": 2000,
    }
    s = StringStretcher("A", "a")
    executor = ThreadPoolExecutor(configs["threads"])
    futures = list()

    for i in range(configs["threads"]):
        futures.append(
            executor.submit(
                s.increment,
                configs["cycles"]
            )
        )

    wait(futures, None, ALL_COMPLETED)

    print(len(s))


if __name__ == "__main__":
    main()