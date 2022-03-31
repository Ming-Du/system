import threading
from concurrent.futures import ThreadPoolExecutor


def task(taskId):
    thread_name = threading.current_thread().getName()
    print "get name:%s,%d\n" %(thread_name,taskId)

def main():
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='Thread')
    for i in range(9999999):
        pool.submit(task, i + 1)


if __name__ == '__main__':
    main()
