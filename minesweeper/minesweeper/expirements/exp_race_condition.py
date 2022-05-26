import threading
from time import sleep


total = 10


def update_total(amount):
    """
    Updates the total by the given amount
    """
    global total
    sleep(0.05)
    total += amount
    print(total)


if __name__ == '__main__':
    for i in range(100):
        my_thread = threading.Thread(target=update_total, args=(5,))
        my_thread.start()
        # NO RACE CONDITION OCCURS, NO MATTER HOW I TWEAK THE CODE!!