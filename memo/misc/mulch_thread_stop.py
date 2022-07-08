from concurrent.futures import ThreadPoolExecutor
import time

def test(n):
    for i in range(100):
        print(f'{n}-{i}')
        time.sleep(2)
        if a == n:
            break


a = 0

executor = ThreadPoolExecutor(max_workers=2)
executor.submit(test, 1)
time.sleep(1)

executor.submit(test, 2)
time.sleep(3)

a = 1