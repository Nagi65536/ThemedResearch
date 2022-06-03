import concurrent.futures
import time


a = 'start'

def print_A():
    global a
    for i in range(10):
        print('A-', a)
        a = f'A{i}'
        time.sleep(2)

def print_B():
    global a
    for i in range(10):
        print('B-', a)
        a = f'B{i}'
        time.sleep(2)


if __name__ == '__main__':
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    executor.submit(print_A)
    time.sleep(1)
    executor.submit(print_B)
